import urllib
from tqdm import tqdm
from huggingface_hub import hf_hub_download
import os

encoder_url = "https://huggingface.co/jan-hq/WhisperVQ/resolve/main/medium_encoder_only.pt"


def _download(url: str, root: str, in_memory: bool):
    os.makedirs(root, exist_ok=True)

    expected_sha256 = url.split("/")[-2]
    download_target = os.path.join(root, os.path.basename(url))

    if os.path.exists(download_target) and not os.path.isfile(download_target):
        raise RuntimeError(
            f"{download_target} exists and is not a regular file")

    if os.path.isfile(download_target):
        with open(download_target, "rb") as f:
            model_bytes = f.read()
        return model_bytes if in_memory else download_target

    with urllib.request.urlopen(url) as source, open(download_target, "wb") as output:
        with tqdm(
            total=int(source.info().get("Content-Length")),
            ncols=80,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as loop:
            while True:
                buffer = source.read(8192)
                if not buffer:
                    break

                output.write(buffer)
                loop.update(len(buffer))

    model_bytes = open(download_target, "rb").read()
    return model_bytes if in_memory else download_target


if not os.path.exists(os.path.dirname(os.path.realpath(__file__))+"/whisper-vq-stoks-v3-7lang-fixed.model"):
    hf_hub_download(
        repo_id="jan-hq/WhisperVQ",
        filename="whisper-vq-stoks-v3-7lang-fixed.model",
        local_dir=".",
    )

_download(encoder_url, os.path.dirname(os.path.realpath(__file__)), False)
