import argparse, os,sys
parser = argparse.ArgumentParser(description="WhisperVQ Application")
parser.add_argument('--log-path', type=str,
                    default='whisper.log', help='The log file path')
parser.add_argument('--log-level', type=str, default='INFO',
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'TRACE'], help='The log level')
parser.add_argument('--port', type=int, default=3348,
                    help='The port to run the WhisperVQ app on')
parser.add_argument('--device-id', type=str, default="0",
                    help='The port to run the WhisperVQ app on')
parser.add_argument('--package-dir', type=str, default="",
                    help='The package-dir to be extended to sys.path')
args = parser.parse_args()
sys.path.insert(0, args.package_dir)
os.environ["CUDA_VISIBLE_DEVICES"] =args.device_id # Use the first Nvidia GPU

import logging
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
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


# after set up logger we can import and use services

from services.AudioTokenizerService import get_audio_tokenizer_service
from routes.AudioTokenizerRoute import audio_tokenizer_router

@asynccontextmanager
async def lifespan(app: FastAPI):
   
    # on startup
    get_audio_tokenizer_service()
    yield
    # on shutdown

app = FastAPI(lifespan=lifespan)

# include the routes
app.include_router(audio_tokenizer_router)

def self_terminate():
    time.sleep(1)
    parent = psutil.Process(psutil.Process(os.getpid()).ppid())
    parent.kill()


@app.delete("/destroy")
async def destroy():
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
    format_info = get_audio_tokenizer_service().get_format_info()
    logger.info("Supported formats:")
    for format, info in format_info.items():
        logger.info(f"{format}: {info}")

    uvicorn.run(app, host="0.0.0.0", port=args.port)
