import argparse
parser = argparse.ArgumentParser(description="WhisperVQ Application")
parser.add_argument('--log-path', type=str,
                    default='whisper.log', help='The log file path')
parser.add_argument('--log-level', type=str, default='INFO',
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'TRACE'], help='The log level')
parser.add_argument('--port', type=int, default=3348,
                    help='The port to run the WhisperVQ app on')
parser.add_argument('--package-dir', type=str, default="",
                    help='The package-dir to be extended to sys.path')
args = parser.parse_args()
import sys
sys.path.insert(0, args.environment)
import tempfile
from typing import Tuple
from enum import Enum
import io
import logging
from custom_component import CustomRQBottleneckTransformer
from whisperspeech.vq_stoks import RQBottleneckTransformer
from huggingface_hub import hf_hub_download
import uvicorn
from transformers import WhisperModel, WhisperProcessor
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException
from contextlib import asynccontextmanager
import torchaudio
import torch
import os
import time
import psutil
import threading


logging.basicConfig(level=args.log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(args.log_path),
                        # logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Use the first GPU


device = "cuda" if torch.cuda.is_available() else "cpu"
if not os.path.exists(os.path.dirname(os.path.realpath(__file__))+"/whisper-vq-stoks-v3-7lang-fixed.model"):
    hf_hub_download(
        repo_id="jan-hq/WhisperVQ",
        filename="whisper-vq-stoks-v3-7lang-fixed.model",
        local_dir=".",
    )
vq_model = CustomRQBottleneckTransformer.load_vq_only(
    os.path.dirname(os.path.realpath(__file__)) +
    "/whisper-vq-stoks-v3-7lang-fixed.model"
).to(device)
vq_model.load_encoder(device)
vq_model.eval()


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield
    # on shutdown


# vq_model = torch.compile(vq_model)


class AudioFormat(str, Enum):
    WAV = "wav"    # Supported by both backends
    MP3 = "mp3"    # Supported by ffmpeg
    FLAC = "flac"  # Supported by both
    AAC = "aac"    # Supported by ffmpeg
    OGG = "ogg"    # Supported by ffmpeg
    OPUS = "opus"  # Supported by ffmpeg
    PCM = "pcm"    # Raw PCM data


# Format to backend mapping
FORMAT_BACKENDS = {
    AudioFormat.WAV: ["soundfile", "ffmpeg"],
    AudioFormat.MP3: ["ffmpeg"],
    AudioFormat.FLAC: ["soundfile", "ffmpeg"],
    AudioFormat.AAC: ["ffmpeg"],
    AudioFormat.OGG: ["ffmpeg"],
    AudioFormat.OPUS: ["ffmpeg"],
    AudioFormat.PCM: ["soundfile"]
}


class AudioProcessor:
    def __init__(self):
        self.available_backends = torchaudio.list_audio_backends()
        logger.info(f"Available backends: {self.available_backends}")

        # Verify ffmpeg support
        self.has_ffmpeg = "ffmpeg" in self.available_backends
        if not self.has_ffmpeg:
            logger.warning(
                "FFMPEG backend not available. Some formats may not be supported")

    def _get_best_backend(self, format: AudioFormat) -> str:
        """Determine the best backend for the given format"""
        supported_backends = FORMAT_BACKENDS[format]
        for backend in supported_backends:
            if backend in self.available_backends:
                return backend
        raise ValueError(f"No available backend supports format {format}")

    async def load_audio(
        self,
        file_obj: bytes,
        format: AudioFormat,
        target_sr: int = 16000
    ) -> Tuple[torch.Tensor, int]:
        """
        Load audio from bytes object with format handling

        Args:
            file_obj: Audio file bytes
            format: Audio format enum
            target_sr: Target sample rate (default: 16000)

        Returns:
            Tuple[torch.Tensor, int]: Audio tensor and sample rate
        """
        try:
            # Get appropriate backend
            backend = self._get_best_backend(format)
            torchaudio.set_audio_backend(backend)
            logger.info(f"Using {backend} backend for {format} format")

            if format == AudioFormat.PCM:
                # Handle raw PCM
                wav = torch.frombuffer(file_obj, dtype=torch.int16)
                wav = wav.float() / 32768.0  # Normalize to [-1, 1]
                wav = wav.unsqueeze(0)  # Add channel dimension
                sr = target_sr
            else:
                # For formats that might need ffmpeg processing
                if os.name == "nt":  # for windows
                    wav, sr = torchaudio.load(io.BytesIO(file_obj))
                else:
                    with tempfile.NamedTemporaryFile(suffix=f".{format}") as temp_file:
                        # Write bytes to temporary file
                        temp_file.write(file_obj)
                        temp_file.flush()

                        # Load audio
                        wav, sr = torchaudio.load(temp_file.name)

            # Convert to mono if stereo
            if wav.shape[0] > 1:
                wav = torch.mean(wav, dim=0, keepdim=True)

            # Resample if needed
            if sr != target_sr:
                wav = torchaudio.functional.resample(wav, sr, target_sr)
                sr = target_sr

            return wav, sr

        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Error processing {format} audio: {str(e)}"
            )

    def get_format_info(self) -> dict:
        """Get information about supported formats"""
        supported_formats = {}
        for format in AudioFormat:
            try:
                backend = self._get_best_backend(format)
                supported_formats[format] = {
                    "supported": True,
                    "backend": backend
                }
            except ValueError:
                supported_formats[format] = {
                    "supported": False,
                    "backend": None
                }
        return supported_formats


audio_processor = AudioProcessor()

app = FastAPI(lifespan=lifespan)


@app.get("/supported_formats")
async def get_supported_formats():
    """Endpoint to check supported formats"""
    return audio_processor.get_format_info()


@app.post("/tokenize/{format}")
async def tokenize_audio(format: AudioFormat = "wav", file: UploadFile = File(...)):
    try:
        # Read file
        file_obj = await file.read()

        # Load and process audio
        wav, sr = await audio_processor.load_audio(file_obj, format)

        # Ensure we're using CUDA if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        wav = wav.to(device)

        # Generate tokens
        with torch.no_grad():
            codes = vq_model.encode_audio(wav)
            codes = codes[0].cpu().tolist()

        # Format result
        result = ''.join(f'<|sound_{num:04d}|>' for num in codes)

        return JSONResponse(content={
            "model_name": "whisper-vq-stoks-v3-7lang-fixed.model",
            "tokens": f'<|sound_start|>{result}<|sound_end|>',
            "format": format,
            "sample_rate": sr,
            "backend_used": audio_processor._get_best_backend(format)
        })

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


def self_terminate():
    time.sleep(1)
    parent = psutil.Process(psutil.Process(os.getpid()).ppid())
    parent.kill()


@app.post("/kill")
async def kill():
    threading.Thread(target=self_terminate, daemon=True).start()
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG

    LOGGING_CONFIG["handlers"]["default"] = {
        "class": "logging.FileHandler",
        "filename": args.log_path,
        "formatter": "default"
    }
    LOGGING_CONFIG["handlers"]["access"] = {
        "class": "logging.FileHandler",
        "filename": args.log_path,
        "formatter": "access"
    }
    LOGGING_CONFIG["loggers"]["uvicorn.error"]["level"] = args.log_level
    LOGGING_CONFIG["loggers"]["uvicorn.access"]["level"] = args.log_level

# Print supported formats at startup
    processor = AudioProcessor()
    format_info = processor.get_format_info()
    logger.info("Supported formats:")
    for format, info in format_info.items():
        logger.info(f"{format}: {info}")

    uvicorn.run(app, host="0.0.0.0", port=args.port)
