from custom_component import _download
from huggingface_hub import hf_hub_download
import os

encoder_url = "https://huggingface.co/jan-hq/WhisperVQ/resolve/main/medium_encoder_only.pt"
if not os.path.exists(os.path.dirname(os.path.realpath(__file__))+"/whisper-vq-stoks-v3-7lang-fixed.model"):
    hf_hub_download(
        repo_id="jan-hq/WhisperVQ",
        filename="whisper-vq-stoks-v3-7lang-fixed.model",
        local_dir=".",
    )

_download(encoder_url,os.path.dirname(os.path.realpath(__file__)), False )
