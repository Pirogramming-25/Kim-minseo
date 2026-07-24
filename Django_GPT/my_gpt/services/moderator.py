from functools import lru_cache

from transformers import pipeline

from .common import get_hf_token, get_pipeline_device


MODEL_ID = "unitary/toxic-bert"


@lru_cache(maxsize=1)
def get_moderation_pipeline():
    return pipeline(
        task="text-classification",
        model=MODEL_ID,
        device=get_pipeline_device(),
        token=get_hf_token(),
        top_k=None,
    )


def analyze_toxicity(text):
    moderator = get_moderation_pipeline()
    raw_result = moderator(text)

    if raw_result and isinstance(raw_result[0], list):
        raw_result = raw_result[0]

    scores = sorted(
        [
            {
                "label": item["label"].lower(),
                "score": float(item["score"]),
            }
            for item in raw_result
        ],
        key=lambda item: item["score"],
        reverse=True,
    )

    highest = scores[0]

    return {
        "highest_label": highest["label"],
        "highest_score": highest["score"],
        "all_scores": scores,
    }