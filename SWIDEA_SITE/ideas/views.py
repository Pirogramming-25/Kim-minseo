from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import DevToolForm, IdeaForm
from .models import DevTool, Idea, IdeaStar


def _session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _starred_ids(request):
    if not request.user.is_authenticated:
        return set()
    return set(_star_queryset(request).values_list("idea_id", flat=True))


def _star_queryset(request):
    return IdeaStar.objects.filter(user=request.user)


def _toggle_star(request, idea):
    star, created = IdeaStar.objects.get_or_create(idea=idea, user=request.user)
    if not created:
        star.delete()
    return created


def _ensure_idea_author(request, idea):
    if idea.author_id != request.user.id:
        raise PermissionDenied


def idea_list(request):
    sort = request.GET.get("sort", "latest")
    query = request.GET.get("q", "").strip()
    show_mine = request.GET.get("mine") == "1" and request.user.is_authenticated
    show_starred = request.GET.get("starred") == "1" and request.user.is_authenticated
    sort_options = {
        "latest": "-created_at",
        "oldest": "created_at",
        "title": "title",
        "interest": "-interest",
        "star": "-star_count",
    }
    ideas = Idea.objects.select_related("author").prefetch_related("devtools").annotate(star_count=Count("stars", distinct=True))

    if show_mine:
        ideas = ideas.filter(author=request.user)

    if show_starred:
        ideas = ideas.filter(pk__in=_star_queryset(request).values("idea_id"))

    if query:
        ideas = ideas.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(devtools__name__icontains=query)
            | Q(devtools__kind__icontains=query)
        ).distinct()

    ideas = ideas.order_by(sort_options.get(sort, "-created_at"), "title")
    paginator = Paginator(ideas, 4)
    page_obj = paginator.get_page(request.GET.get("page"))
    starred_ids = _starred_ids(request)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    template_name = "ideas/_idea_list_content.html" if is_ajax else "ideas/idea_list.html"
    return render(
        request,
        template_name,
        {
            "page_obj": page_obj,
            "ideas": page_obj.object_list,
            "selected_sort": sort,
            "query": query,
            "show_mine": show_mine,
            "show_starred": show_starred,
            "list_querystring": request.GET.urlencode(),
            "starred_ids": starred_ids,
        },
    )


def idea_detail(request, pk):
    idea = get_object_or_404(
        Idea.objects.select_related("author").prefetch_related("devtools").annotate(star_count=Count("stars", distinct=True)),
        pk=pk,
    )
    previous_idea = (
        Idea.objects.filter(Q(created_at__gt=idea.created_at) | Q(created_at=idea.created_at, pk__gt=idea.pk))
        .order_by("created_at", "pk")
        .first()
    )
    next_idea = (
        Idea.objects.filter(Q(created_at__lt=idea.created_at) | Q(created_at=idea.created_at, pk__lt=idea.pk))
        .order_by("-created_at", "-pk")
        .first()
    )
    is_starred = idea.pk in _starred_ids(request)
    back_url = request.GET.get("next") or None
    return render(
        request,
        "ideas/idea_detail.html",
        {
            "idea": idea,
            "is_starred": is_starred,
            "previous_idea": previous_idea,
            "next_idea": next_idea,
            "can_edit": idea.author_id == request.user.id,
            "back_url": back_url,
        },
    )


@login_required
def idea_create(request):
    if not DevTool.objects.exists():
        return render(request, "ideas/idea_form.html", {"no_devtools": True, "is_update": False})

    if request.method == "POST":
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = request.user
            idea.save()
            form.save_m2m()
            return redirect(idea.get_absolute_url())
    else:
        form = IdeaForm()
    return render(request, "ideas/idea_form.html", {"form": form, "is_update": False})


@login_required
def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    _ensure_idea_author(request, idea)

    if request.method == "POST":
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            idea = form.save()
            return redirect(idea.get_absolute_url())
    else:
        form = IdeaForm(instance=idea)
    return render(request, "ideas/idea_form.html", {"form": form, "idea": idea, "is_update": True})


@login_required
@require_POST
def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    _ensure_idea_author(request, idea)

    _delete_idea_image(idea)
    idea.delete()
    return redirect("ideas:idea_list")


def _delete_idea_image(idea):
    if idea.image:
        idea.image.delete(save=False)


@require_POST
@login_required
def idea_star_toggle(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    created = _toggle_star(request, idea)
    return JsonResponse({"starred": created, "star_count": idea.stars.count()})


@require_POST
def idea_interest_change(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    try:
        amount = int(request.POST.get("amount", 0))
    except ValueError:
        amount = 0
    idea.interest = max(0, idea.interest + amount)
    idea.save(update_fields=["interest", "updated_at"])
    return JsonResponse({"interest": idea.interest})


def devtool_list(request):
    query = request.GET.get("q", "").strip()
    devtools = DevTool.objects.annotate(idea_count=Count("ideas", distinct=True))
    if query:
        devtools = devtools.filter(
            Q(name__icontains=query) | Q(kind__icontains=query) | Q(content__icontains=query)
        )
    return render(
        request,
        "ideas/devtool_list.html",
        {"devtools": devtools, "query": query},
    )


def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool.objects.prefetch_related("ideas"), pk=pk)
    return render(request, "ideas/devtool_detail.html", {"devtool": devtool})


def devtool_create(request):
    if request.method == "POST":
        form = DevToolForm(request.POST)
        if form.is_valid():
            devtool = form.save()
            return redirect(devtool.get_absolute_url())
    else:
        form = DevToolForm()
    return render(request, "ideas/devtool_form.html", {"form": form, "is_update": False})


def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    if request.method == "POST":
        form = DevToolForm(request.POST, instance=devtool)
        if form.is_valid():
            devtool = form.save()
            return redirect(devtool.get_absolute_url())
    else:
        form = DevToolForm(instance=devtool)
    return render(
        request,
        "ideas/devtool_form.html",
        {"form": form, "devtool": devtool, "is_update": True},
    )


@require_POST
def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    devtool.delete()
    return redirect("ideas:devtool_list")
