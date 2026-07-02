from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReviewForm
from .models import Review


def review_list(request):
    sort = request.GET.get("sort", "recent")
    query = request.GET.get("q", "").strip()
    sort_options = {
        "recent": "-created_at",
        "rating": "-rating",
        "running_time": "running_time",
        "title": "title",
    }
    reviews = Review.objects.all()
    if query:
        reviews = reviews.filter(
            Q(title__icontains=query)
            | Q(director__icontains=query)
            | Q(actor__icontains=query)
            | Q(genre__icontains=query)
        )
    reviews = reviews.order_by(sort_options.get(sort, "-created_at"))
    context = {
        "reviews": reviews,
        "selected_sort": sort,
        "query": query,
    }
    return render(request, "reviews/review_list.html", context)


def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "reviews/review_detail.html", {"review": review})


def review_create(request):
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("reviews:index")
    else:
        form = ReviewForm()
    return render(request, "reviews/review_form.html", {"form": form, "is_update": False})


def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect("reviews:detail", pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, "reviews/review_form.html", {"form": form, "is_update": True})


def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
        return redirect("reviews:index")
    return redirect("reviews:detail", pk=review.pk)
