from pydantic import BaseModel
from enum import Enum 

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
