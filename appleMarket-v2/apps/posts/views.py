import os
import tempfile

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PostForm
from .models import Post
from .services.hashtag_service import analyze_product_image
from .services.ocr_service import analyze_nutrition_image


def main(request):
    posts = Post.objects.all().order_by("-created_at")

    search_txt = request.GET.get("search_txt", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    hashtag = request.GET.get("hashtag", "").strip().lstrip("#")

    if search_txt:
        posts = posts.filter(
            title__icontains=search_txt
        )

    if hashtag:
        posts = posts.filter(
            hashtags__icontains=f"#{hashtag}"
        )

    try:
        if min_price:
            posts = posts.filter(
                price__gte=int(min_price)
            )

        if max_price:
            posts = posts.filter(
                price__lte=int(max_price)
            )

    except (ValueError, TypeError):
        pass

    context = {
        "posts": posts,
        "search_txt": search_txt,
        "min_price": min_price,
        "max_price": max_price,
        "hashtag": hashtag,
    }

    return render(
        request,
        "posts/list.html",
        context,
    )


def create(request):
    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            post = form.save()

            return redirect(
                "posts:detail",
                pk=post.pk,
            )

    else:
        form = PostForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "posts/create.html",
        context,
    )


def detail(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
    )

    context = {
        "post": post,
    }

    return render(
        request,
        "posts/detail.html",
        context,
    )


def update(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
    )

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post,
        )

        if form.is_valid():
            updated_post = form.save()

            return redirect(
                "posts:detail",
                pk=updated_post.pk,
            )

    else:
        form = PostForm(
            instance=post,
        )

    context = {
        "form": form,
        "post": post,
    }

    return render(
        request,
        "posts/update.html",
        context,
    )


def delete(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
    )

    post.delete()

    return redirect(
        "posts:main"
    )


def save_uploaded_file(uploaded_file):
    suffix = (
        os.path.splitext(
            uploaded_file.name
        )[1]
        or ".jpg"
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)

        return temp_file.name


@require_POST
def analyze_nutrition(request):
    uploaded_image = request.FILES.get(
        "nutrition_image"
    )

    if uploaded_image is None:
        return JsonResponse(
            {
                "error": (
                    "영양성분표 이미지를 "
                    "선택해주세요."
                )
            },
            status=400,
        )

    temp_path = None

    try:
        temp_path = save_uploaded_file(
            uploaded_image
        )

        result = analyze_nutrition_image(
            temp_path
        )

        return JsonResponse(
            result
        )

    except Exception as error:
        return JsonResponse(
            {
                "error": (
                    "OCR 처리 중 오류가 "
                    f"발생했습니다: {error}"
                )
            },
            status=500,
        )

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)


@require_POST
def analyze_hashtags(request):
    uploaded_image = request.FILES.get(
        "photo"
    )

    if uploaded_image is None:
        return JsonResponse(
            {
                "error": (
                    "상품 이미지를 "
                    "선택해주세요."
                )
            },
            status=400,
        )

    temp_path = None

    try:
        temp_path = save_uploaded_file(
            uploaded_image
        )

        hashtags = analyze_product_image(
            temp_path
        )

        hashtag_text = " ".join(
            f"#{tag}"
            for tag in hashtags
        )

        return JsonResponse(
            {
                "hashtags": hashtags,
                "hashtag_text": hashtag_text,
            }
        )

    except Exception as error:
        return JsonResponse(
            {
                "error": (
                    "해시태그 분석 중 오류가 "
                    f"발생했습니다: {error}"
                )
            },
            status=500,
        )

    finally:
        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(temp_path)