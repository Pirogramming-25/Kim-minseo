from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm
from ideas.models import IdeaStar


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:mypage")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def mypage(request):
    starred_ideas = (
        IdeaStar.objects.filter(user=request.user)
        .select_related("idea")
        .prefetch_related("idea__devtools")
        .order_by("-created_at")
    )
    return render(request, "accounts/mypage.html", {"starred_ideas": starred_ideas})
