from .moderator import analyze_toxicity
from .sentiment import analyze_sentiment
from .summarizer import summarize_text


def create_final_judgment(sentiment, toxicity):
    sentiment_label = sentiment["label"]
    toxicity_score = toxicity["highest_score"]

    if sentiment_label == "negative":
        sentiment_description = "부정적인 평가를 포함합니다."
    elif sentiment_label == "positive":
        sentiment_description = "긍정적인 평가를 포함합니다."
    else:
        sentiment_description = "중립적인 평가를 포함합니다."

    if toxicity_score >= 0.5:
        toxicity_description = "유해 표현 가능성이 높습니다."
    else:
        toxicity_description = "심각한 유해 표현 가능성은 낮습니다."

    return f"{sentiment_description} {toxicity_description}"


def analyze_customer_feedback(text, regenerate=False):
    summary_result = summarize_text(
        text,
        regenerate=regenerate,
    )

    summary = summary_result["summary"]

    sentiment_result = analyze_sentiment(summary)
    toxicity_result = analyze_toxicity(summary)

    judgment = create_final_judgment(
        sentiment_result,
        toxicity_result,
    )

    return {
        "original_text": text,
        "summary": summary,
        "sentiment": sentiment_result,
        "toxicity": toxicity_result,
        "judgment": judgment,
    }