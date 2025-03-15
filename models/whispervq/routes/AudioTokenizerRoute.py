from services.AudioTokenizerService import get_audio_tokenizer_service
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import File, UploadFile
from models.audio import AudioFormat, FORMAT_BACKENDS

audio_tokenizer_router = APIRouter(
    prefix="/tokenize", tags=["audio"])


@audio_tokenizer_router.post("/{format}")
async def tokenize_audio(format: AudioFormat = "wav", file: UploadFile = File(...)):
    file_obj = await file.read()
    get_audio_tokenizer_service().tokenize(file_obj, format)
    return get_audio_tokenizer_service().tokenize(file_obj, format)


@audio_tokenizer_router.get("/supported_formats")
async def get_supported_formats():
    return get_audio_tokenizer_service().get_format_info()
