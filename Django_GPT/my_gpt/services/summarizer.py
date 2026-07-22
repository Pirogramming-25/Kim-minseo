from functools import lru_cache

from transformers import pipeline

from .common import get_hf_token, get_pipeline_device


MODEL_ID = "sshleifer/distilbart-cnn-6-6"


@lru_cache(maxsize=1)
def get_summarization_pipeline():
    return pipeline(
        task="summarization",
        model=MODEL_ID,
        device=get_pipeline_device(),
        token=get_hf_token(),
    )


def summarize_text(text, regenerate=False):
    summarizer = get_summarization_pipeline()

    options = {
        "max_length": 180,
        "min_length": 40,
        "do_sample": regenerate,
        "truncation": True,
    }

    if regenerate:
        options.update(
            {
                "top_p": 0.9,
                "temperature": 0.8,
            }
        )

    result = summarizer(text, **options)
    summary = result[0]["summary_text"].strip()

    original_length = len(text)
    summary_length = len(summary)
    summary_ratio = (
        summary_length / original_length * 100
        if original_length
        else 0
    )

    return {
        "summary": summary,
        "original_length": original_length,
        "summary_length": summary_length,
        "summary_ratio": round(summary_ratio, 2),
    }