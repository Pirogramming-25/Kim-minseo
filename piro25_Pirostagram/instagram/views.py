import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import PostForm, ProfileAvatarForm, StoryImageForm
from .models import Comment, Follow, Post, Profile, Story, StoryImage


SORT_OPTIONS = [
    {"value": "recent", "label": "최신순"},
    {"value": "likes", "label": "좋아요순"},
    {"value": "comments", "label": "댓글순"},
]

DEFAULT_USER = {
    "username": "minseo",
    "first_name": "김민서",
    "color": "#d4a5a5",
}


def ensure_profile(user, display_name="", color="#d4a5a5"):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"display_name": display_name or user.username, "color": color},
    )
    changed = False
    if display_name and not profile.display_name:
        profile.display_name = display_name
        changed = True
    if color and profile.color == "#d4a5a5" and color != "#d4a5a5":
        profile.color = color
        changed = True
    if changed:
        profile.save()
    return profile


def get_current_user(request):
    if request.user.is_authenticated:
        ensure_profile(request.user, request.user.first_name or request.user.username)
        return request.user

    user = (
        User.objects.filter(username=DEFAULT_USER["username"]).first()
        or User.objects.filter(is_superuser=True).order_by("id").first()
        or User.objects.order_by("id").first()
    )
    if user:
        ensure_profile(user, user.first_name or user.username)
        return user

    user = User.objects.create(username=DEFAULT_USER["username"], first_name=DEFAULT_USER["first_name"])
    user.set_unusable_password()
    user.save()
    ensure_profile(user, DEFAULT_USER["first_name"], DEFAULT_USER["color"])
    return user


def time_label(created_at):
    diff = timezone.now() - created_at
    if diff < timedelta(minutes=1):
        return "방금 전"
    if diff < timedelta(hours=1):
        return f"{int(diff.total_seconds() // 60)}분 전"
    if diff < timedelta(days=1):
        return f"{int(diff.total_seconds() // 3600)}시간 전"
    return f"{diff.days}일 전"


def post_to_dict(post, current_user):
    profile = ensure_profile(post.author)
    comments = list(post.comments.filter(parent__isnull=True).select_related("author"))
    comment_dicts = [comment_to_dict(comment, current_user) for comment in comments]
    image = post.images.first()
    like_count = post.likes.count()
    return {
        "id": post.id,
        "author": post.author.username,
        "author_url": reverse("instagram:profile") if post.author_id == current_user.id else reverse("instagram:user_profile", args=[post.author.username]),
        "initial": profile.initial,
        "avatar_color": profile.color,
        "avatar_url": profile.avatar.url if profile.avatar else "",
        "location": post.location or "서울",
        "likes": like_count,
        "likes_display": f"{like_count:,}",
        "liked_by_me": post.likes.filter(pk=current_user.pk).exists(),
        "saved_by_me": post.saved_by.filter(pk=current_user.pk).exists(),
        "caption": post.caption,
        "comments": comment_dicts,
        "comment_count": post.comments.count(),
        "visible_comments": comment_dicts[:1],
        "hidden_comments": comment_dicts[1:],
        "time": time_label(post.created_at),
        "preview_only": False,
        "can_edit": post.author_id == current_user.id,
        "image_url": image.image.url if image else "",
    }


def comment_to_dict(comment, current_user):
    return {
        "id": comment.id,
        "author": comment.author.username,
        "content": comment.content,
        "can_edit": comment.author_id == current_user.id,
        "edit_url": reverse("instagram:comment_update", args=[comment.id]),
        "delete_url": reverse("instagram:comment_delete", args=[comment.id]),
        "parent_id": comment.parent_id,
        "replies": [comment_to_dict(reply, current_user) for reply in comment.replies.select_related("author")],
    }


def profile_context(user, current_user):
    profile = ensure_profile(user, user.first_name or user.username)
    return {
        "name": profile.display_name or user.first_name or user.username,
        "username": user.username,
        "initial": profile.initial,
        "color": profile.color,
        "avatar_url": profile.avatar.url if profile.avatar else "",
        "post_count": user.posts.count(),
        "followers": user.follower_relations.count(),
        "following": user.following_relations.count(),
        "bio": profile.bio or "소개글이 없습니다.",
        "is_following": Follow.objects.filter(follower=current_user, following=user).exists(),
    }


def stories_context(current_user):
    profile = ensure_profile(current_user, current_user.first_name or current_user.username)
    result = [
        {
            "username": "스토리 +",
            "initial": profile.initial,
            "color": profile.color,
            "image_url": "",
            "images_json": "[]",
            "avatar_url": profile.avatar.url if profile.avatar else "",
            "is_self": True,
        }
    ]

    following_ids = Follow.objects.filter(follower=current_user).values_list("following_id", flat=True)
    stories = (
        Story.objects.filter(author_id__in=following_ids)
        .select_related("author", "author__profile")
        .prefetch_related("images")
        .order_by("author_id", "-created_at")
    )
    seen = set()
    for story in stories:
        if story.author_id in seen:
            continue
        seen.add(story.author_id)
        images = [
            {"url": story_image.image.url if story_image.image else "", "color": story_image.color}
            for story_image in story.images.all()
        ]
        image = story.images.first()
        profile = ensure_profile(story.author)
        result.append(
            {
                "username": story.author.username,
                "initial": profile.initial,
                "color": image.color if image else profile.color,
                "avatar_url": profile.avatar.url if profile.avatar else "",
                "image_url": image.image.url if image and image.image else "",
                "images_json": json.dumps(images),
                "is_self": False,
            }
        )
    return result


def suggestions_context(current_user):
    following_ids = Follow.objects.filter(follower=current_user).values_list("following_id", flat=True)
    users = (
        User.objects.exclude(pk=current_user.pk)
        .exclude(pk__in=following_ids)
        .select_related("profile")
        .order_by("username")[:5]
    )
    suggestions = []
    for user in users:
        profile = ensure_profile(user, user.first_name or user.username)
        suggestions.append(
            {
                "username": user.username,
                "name": profile.display_name or user.first_name or user.username,
                "initial": profile.initial,
                "color": profile.color,
                "avatar_url": profile.avatar.url if profile.avatar else "",
                "is_following": False,
            }
        )
    return suggestions


def highlights_context():
    return [
        {"label": "하이라이트", "color": "#c8b8a2"},
        {"label": "하이라이트", "color": "#a2b4c8"},
        {"label": "신규", "is_new": True},
    ]


def sorted_posts(queryset, sort):
    if sort == "likes":
        return queryset.annotate(like_total=Count("likes")).order_by("-like_total", "-created_at")
    if sort == "comments":
        return queryset.annotate(comment_total=Count("comments")).order_by("-comment_total", "-created_at")
    return queryset.order_by("-created_at")


def base_context(request):
    current_user = get_current_user(request)
    return {
        "current_user": current_user,
        "profile": profile_context(current_user, current_user),
        "stories": stories_context(current_user),
        "suggestions": suggestions_context(current_user),
        "highlights": highlights_context(),
        "sort_options": SORT_OPTIONS,
    }


def index(request):
    context = base_context(request)
    current_user = context["current_user"]
    following_ids = Follow.objects.filter(follower=current_user).values_list("following_id", flat=True)
    sort = request.GET.get("sort", "recent")
    queryset = Post.objects.filter(Q(author=current_user) | Q(author_id__in=following_ids)).select_related("author")
    posts = [post_to_dict(post, current_user) for post in sorted_posts(queryset, sort)]
    context.update({"active_page": "home", "posts": posts, "selected_sort": sort})
    return render(request, "instagram/index.html", context)


def profile(request):
    context = base_context(request)
    current_user = context["current_user"]
    current_tab = request.GET.get("tab", "posts")
    if current_tab == "saved":
        queryset = current_user.saved_posts.prefetch_related("images")
    else:
        current_tab = "posts"
        queryset = current_user.posts.prefetch_related("images")
    profile_posts = [profile_post_dict(post) for post in queryset]
    context.update({"active_page": "profile", "profile_posts": profile_posts, "current_tab": current_tab})
    return render(request, "instagram/profile.html", context)


@require_POST
def profile_avatar_update(request):
    current_user = get_current_user(request)
    profile = ensure_profile(current_user, current_user.first_name or current_user.username)
    form = ProfileAvatarForm(request.POST, request.FILES, instance=profile)
    if form.is_valid():
        form.save()
    return redirect("instagram:profile")


def profile_post_dict(post):
    image = post.images.first()
    return {"id": post.id, "image_url": image.image.url if image else ""}


def user_profile(request, username):
    context = base_context(request)
    current_user = context["current_user"]
    user = get_object_or_404(User, username=username)
    other_user_posts = [profile_post_dict(post) for post in user.posts.prefetch_related("images")]
    context.update(
        {
            "active_page": "user_search",
            "other_user": profile_context(user, current_user),
            "other_user_posts": other_user_posts,
        }
    )
    return render(request, "instagram/user_profile.html", context)


def post_search(request):
    context = base_context(request)
    current_user = context["current_user"]
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "recent")
    queryset = Post.objects.select_related("author")
    if query:
        queryset = queryset.filter(
            Q(caption__icontains=query) | Q(location__icontains=query) | Q(author__username__icontains=query)
        )
    context.update(
        {
            "active_page": "post_search",
            "query": query,
            "selected_sort": sort,
            "posts": [post_to_dict(post, current_user) for post in sorted_posts(queryset, sort)],
        }
    )
    return render(request, "instagram/post_search.html", context)


def user_search(request):
    context = base_context(request)
    current_user = context["current_user"]
    query = request.GET.get("q", "").strip()
    users = User.objects.none()
    if query:
        users = User.objects.exclude(pk=current_user.pk).select_related("profile")
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(profile__display_name__icontains=query))
    context.update(
        {
            "active_page": "user_search",
            "query": query,
            "search_users": [user_result_dict(user, current_user) for user in users.distinct()],
        }
    )
    return render(request, "instagram/user_search.html", context)


def user_result_dict(user, current_user):
    profile = ensure_profile(user, user.first_name or user.username)
    return {
        "username": user.username,
        "name": profile.display_name or user.first_name or user.username,
        "initial": profile.initial,
        "color": profile.color,
        "avatar_url": profile.avatar.url if profile.avatar else "",
        "is_following": Follow.objects.filter(follower=current_user, following=user).exists(),
    }


def post_create(request):
    context = base_context(request)
    current_user = context["current_user"]
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save(author=current_user)
        return redirect("instagram:index")
    context.update(
        {
            "active_page": "post_create",
            "form_title": "게시글 만들기",
            "submit_label": "공유하기",
            "is_edit": False,
            "form": form,
        }
    )
    return render(request, "instagram/post_form.html", context)


def story_create(request):
    context = base_context(request)
    current_user = context["current_user"]
    form = StoryImageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        story = Story.objects.create(author=current_user)
        color = ensure_profile(current_user).color
        for image in form.cleaned_data["images"]:
            StoryImage.objects.create(story=story, image=image, color=color)
        return redirect("instagram:index")
    context.update(
        {
            "active_page": "home",
            "form": form,
            "form_title": "스토리 만들기",
            "submit_label": "스토리 공유",
        }
    )
    return render(request, "instagram/story_form.html", context)


def post_edit(request, post_id):
    context = base_context(request)
    current_user = context["current_user"]
    post = get_object_or_404(Post, pk=post_id, author=current_user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save(author=current_user)
        return redirect("instagram:index")
    image = post.images.first()
    context.update(
        {
            "active_page": "post_create",
            "form_title": "게시글 수정",
            "submit_label": "수정하기",
            "is_edit": True,
            "post_id": post_id,
            "post": post,
            "post_image_url": image.image.url if image else "",
            "form": form,
        }
    )
    return render(request, "instagram/post_form.html", context)


@require_POST
def post_delete(request, post_id):
    current_user = get_current_user(request)
    post = get_object_or_404(Post, pk=post_id, author=current_user)
    post.delete()
    return redirect("instagram:index")


@require_POST
def post_like(request, post_id):
    current_user = get_current_user(request)
    post = get_object_or_404(Post, pk=post_id)
    if post.likes.filter(pk=current_user.pk).exists():
        post.likes.remove(current_user)
        liked = False
    else:
        post.likes.add(current_user)
        liked = True
    like_count = post.likes.count()
    return JsonResponse({"liked": liked, "like_count": like_count, "like_text": f"좋아요 {like_count:,}개"})


@require_POST
def post_save(request, post_id):
    current_user = get_current_user(request)
    post = get_object_or_404(Post, pk=post_id)
    if post.saved_by.filter(pk=current_user.pk).exists():
        post.saved_by.remove(current_user)
        saved = False
    else:
        post.saved_by.add(current_user)
        saved = True
    return JsonResponse({"saved": saved})


@require_POST
def follow_toggle(request, username):
    current_user = get_current_user(request)
    target = get_object_or_404(User, username=username)
    if current_user == target:
        return JsonResponse({"error": "자기 자신은 팔로우할 수 없습니다."}, status=400)
    relation = Follow.objects.filter(follower=current_user, following=target)
    if relation.exists():
        relation.delete()
        following = False
    else:
        Follow.objects.create(follower=current_user, following=target)
        following = True
    return JsonResponse({"following": following, "followers": target.follower_relations.count()})


@require_POST
def comment_create(request, post_id):
    current_user = get_current_user(request)
    post = get_object_or_404(Post, pk=post_id)
    content = request.POST.get("content", "").strip()
    parent_id = request.POST.get("parent_id")
    if not content:
        return JsonResponse({"error": "댓글 내용을 입력하세요."}, status=400)
    parent = Comment.objects.filter(pk=parent_id, post=post).first() if parent_id else None
    comment = Comment.objects.create(post=post, author=current_user, content=content, parent=parent)
    return JsonResponse({"comment": comment_to_dict(comment, current_user), "comment_count": post.comments.count()})


@require_POST
def comment_update(request, comment_id):
    current_user = get_current_user(request)
    comment = get_object_or_404(Comment, pk=comment_id, author=current_user)
    content = request.POST.get("content", "").strip()
    if not content:
        return JsonResponse({"error": "댓글 내용을 입력하세요."}, status=400)
    comment.content = content
    comment.save()
    return JsonResponse({"comment": comment_to_dict(comment, current_user)})


@require_POST
def comment_delete(request, comment_id):
    current_user = get_current_user(request)
    comment = get_object_or_404(Comment, pk=comment_id, author=current_user)
    post = comment.post
    comment.delete()
    return JsonResponse({"deleted": True, "comment_count": post.comments.count()})
