import json
import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import model_login_required
from .models import InferenceHistory
from .services.combo import analyze_customer_feedback
from .services.moderator import analyze_toxicity
from .services.sentiment import analyze_sentiment
from .services.summarizer import summarize_text


logger = logging.getLogger(__name__)

MODEL_ERROR_MESSAGE = (
    "모델 실행에 실패했습니다. "
    "잠시 후 다시 시도해주세요."
)


def home(request):
    return redirect("my_gpt:sentiment")


def get_histories(request, task):
    if not request.user.is_authenticated:
        return []

    return (
        InferenceHistory.objects
        .filter(
            user=request.user,
            task=task,
        )
        .order_by("-created_at")[:5]
    )


def sentiment_page(request):
    histories = get_histories(
        request,
        InferenceHistory.Task.SENTIMENT,
    )

    return render(
        request,
        "my_gpt/sentiment.html",
        {
            "active_tab": "sentiment",
            "histories": histories,
        },
    )


@model_login_required
def summarize_page(request):
    histories = get_histories(
        request,
        InferenceHistory.Task.SUMMARIZE,
    )

    return render(
        request,
        "my_gpt/summarize.html",
        {
            "active_tab": "summarize",
            "histories": histories,
        },
    )


@model_login_required
def moderate_page(request):
    histories = get_histories(
        request,
        InferenceHistory.Task.MODERATE,
    )

    return render(
        request,
        "my_gpt/moderate.html",
        {
            "active_tab": "moderate",
            "histories": histories,
        },
    )


@model_login_required
def combo_page(request):
    histories = get_histories(
        request,
        InferenceHistory.Task.COMBO,
    )

    return render(
        request,
        "my_gpt/combo.html",
        {
            "active_tab": "combo",
            "histories": histories,
        },
    )


def parse_json_request(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return None, JsonResponse(
            {
                "error": "올바른 요청 형식이 아닙니다.",
            },
            status=400,
        )

    if not isinstance(data, dict):
        return None, JsonResponse(
            {
                "error": "올바른 요청 형식이 아닙니다.",
            },
            status=400,
        )

    return data, None


def get_text_value(data):
    text = data.get("text")

    if not isinstance(text, str):
        return None, JsonResponse(
            {
                "error": "텍스트 형식으로 입력해주세요.",
            },
            status=400,
        )

    return text.strip(), None


def save_history(
    request,
    task,
    input_text,
    output_text,
    result_data,
):
    if not request.user.is_authenticated:
        return None

    return InferenceHistory.objects.create(
        user=request.user,
        task=task,
        input_text=input_text,
        output_text=output_text,
        result_data=result_data,
    )


@require_POST
def run_sentiment(request):
    data, error_response = parse_json_request(request)

    if error_response:
        return error_response

    text, error_response = get_text_value(data)

    if error_response:
        return error_response

    if not text:
        return JsonResponse(
            {
                "error": "분석할 문장을 입력해주세요.",
            },
            status=400,
        )

    if len(text) > 1000:
        return JsonResponse(
            {
                "error": "문장은 1,000자 이하로 입력해주세요.",
            },
            status=400,
        )

    try:
        result = analyze_sentiment(text)
    except Exception:
        logger.exception("Sentiment inference failed.")

        return JsonResponse(
            {
                "error": MODEL_ERROR_MESSAGE,
            },
            status=502,
        )

    save_history(
        request=request,
        task=InferenceHistory.Task.SENTIMENT,
        input_text=text,
        output_text=result["label"],
        result_data=result,
    )

    return JsonResponse(
        {
            "input_text": text,
            "result": result,
        }
    )


@require_POST
@model_login_required
def run_summarize(request):
    data, error_response = parse_json_request(request)

    if error_response:
        return error_response

    text, error_response = get_text_value(data)

    if error_response:
        return error_response

    if len(text) < 100:
        return JsonResponse(
            {
                "error": (
                    "요약할 문서는 100자 이상 "
                    "입력해주세요."
                ),
            },
            status=400,
        )

    if len(text) > 5000:
        return JsonResponse(
            {
                "error": (
                    "문서는 5,000자 이하로 "
                    "입력해주세요."
                ),
            },
            status=400,
        )

    try:
        result = summarize_text(text)
    except Exception:
        logger.exception("Summarization inference failed.")

        return JsonResponse(
            {
                "error": MODEL_ERROR_MESSAGE,
            },
            status=502,
        )

    save_history(
        request=request,
        task=InferenceHistory.Task.SUMMARIZE,
        input_text=text,
        output_text=result["summary"],
        result_data=result,
    )

    return JsonResponse(
        {
            "input_text": text,
            "result": result,
        }
    )


@require_POST
@model_login_required
def run_moderate(request):
    data, error_response = parse_json_request(request)

    if error_response:
        return error_response

    text, error_response = get_text_value(data)

    if error_response:
        return error_response

    if not text:
        return JsonResponse(
            {
                "error": (
                    "분석할 문장을 입력해주세요."
                ),
            },
            status=400,
        )

    if len(text) > 1000:
        return JsonResponse(
            {
                "error": (
                    "문장은 1,000자 이하로 "
                    "입력해주세요."
                ),
            },
            status=400,
        )

    try:
        result = analyze_toxicity(text)
    except Exception:
        logger.exception("Moderation inference failed.")

        return JsonResponse(
            {
                "error": MODEL_ERROR_MESSAGE,
            },
            status=502,
        )

    save_history(
        request=request,
        task=InferenceHistory.Task.MODERATE,
        input_text=text,
        output_text=result["highest_label"],
        result_data=result,
    )

    return JsonResponse(
        {
            "input_text": text,
            "result": result,
        }
    )


@require_POST
@model_login_required
def run_combo(request):
    data, error_response = parse_json_request(request)

    if error_response:
        return error_response

    text, error_response = get_text_value(data)

    if error_response:
        return error_response

    regenerate = data.get("regenerate", False)

    if not isinstance(regenerate, bool):
        return JsonResponse(
            {
                "error": (
                    "재생성 값의 형식이 "
                    "올바르지 않습니다."
                ),
            },
            status=400,
        )

    if len(text) < 200:
        return JsonResponse(
            {
                "error": (
                    "고객 피드백은 200자 이상 "
                    "입력해주세요."
                ),
            },
            status=400,
        )

    if len(text) > 5000:
        return JsonResponse(
            {
                "error": (
                    "고객 피드백은 5,000자 이하로 "
                    "입력해주세요."
                ),
            },
            status=400,
        )

    try:
        result = analyze_customer_feedback(
            text,
            regenerate=regenerate,
        )
    except Exception:
        logger.exception("Combo inference failed.")

        return JsonResponse(
            {
                "error": MODEL_ERROR_MESSAGE,
            },
            status=502,
        )

    save_history(
        request=request,
        task=InferenceHistory.Task.COMBO,
        input_text=text,
        output_text=result["summary"],
        result_data=result,
    )

    return JsonResponse(
        {
            "input_text": text,
            "regenerated": regenerate,
            "result": result,
        }
    )