import os

import torch


def get_pipeline_device():
    if torch.cuda.is_available():
        return 0

    if (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    ):
        return "mps"

    return -1


def get_hf_token():
    token = os.getenv("HF_TOKEN", "").strip()
    return token or None