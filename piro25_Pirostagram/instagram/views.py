from django.shortcuts import render


def get_sample_data():
    profile = {
        "name": "김민서",
        "username": "minseoooo_k",
        "initial": "김",
        "post_count": 12,
        "followers": 446,
        "following": 316,
    }
    stories = [
        {"username": "스토리 +", "initial": "M", "color": "#9fd3ca", "is_self": True},
        {"username": "Piro", "initial": "I", "color": "#c1a4d7"},
        {"username": "Piroo", "initial": "I", "color": "#bca1dc"},
        {"username": "Piro_3", "initial": "Y", "color": "#9fb3d5"},
        {"username": "Piro_2", "initial": "S", "color": "#d5cb93"},
        {"username": "Piro_1", "initial": "P", "color": "#9bd0ad"},
    ]
    posts = [
        {
            "author": "minseo_k",
            "initial": "M",
            "avatar_color": "#9fd3ca",
            "location": "서울",
            "likes": 1284,
            "likes_display": "1,284",
            "caption": "🌸 오늘도 좋은 하루!",
            "comments": [
                {"author": "Piro_1", "content": "어디야? 나도 가고 싶다!!"},
                {"author": "yyy__", "content": "너무 예쁘다 🌸"},
                {"author": "ssss_", "content": "같이 가고 싶다 ㅠㅠ"},
            ],
            "visible_comments": [
                {"author": "Piro_1", "content": "어디야? 나도 가고 싶다!!"},
            ],
            "time": "2시간 전",
            "id": 1,
            "can_edit": True,
        },
        {
            "author": "minseo_k",
            "initial": "M",
            "avatar_color": "#9fd3ca",
            "location": "서울",
            "likes": 847,
            "likes_display": "847",
            "caption": "좋은 날 ☀️",
            "comments": [
                {"author": "Piro_3", "content": "완전 좋다!!"},
                {"author": "d_ddd", "content": "부럽다 🥺"},
            ],
            "visible_comments": [],
            "time": "5시간 전",
            "preview_only": True,
            "id": 2,
            "can_edit": True,
        },
    ]
    suggestions = [
        {"username": "j.__", "initial": "J", "color": "#9bd0ad"},
        {"username": "ssss_", "initial": "S", "color": "#d5cb93"},
        {"username": "yyy__", "initial": "Y", "color": "#9fb3d5"},
        {"username": "d_ddd", "initial": "J", "color": "#c1a4d7"},
        {"username": "hhh_", "initial": "H", "color": "#9bd0ad"},
    ]
    highlights = [
        {"label": "하이라이트", "color": "#c8b8a2"},
        {"label": "하이라이트", "color": "#a2b4c8"},
        {"label": "신규", "is_new": True},
    ]
    profile_posts = [{"id": index} for index in range(1, 13)]
    search_users = [
        {"username": "Pirouser1", "name": "pirouser", "initial": "P", "color": "#b9e6bf", "is_following": False},
        {"username": "Pirouser2", "name": "Pirouser2", "initial": "P", "color": "#d4a777", "is_following": False},
        {"username": "pirouser3", "name": "pirouser3", "initial": "P", "color": "#c8b8a2", "is_following": True},
        {"username": "pirouser4", "name": "pirouser4", "initial": "P", "color": "#a2b4c8", "is_following": True},
    ]
    return {
        "profile": profile,
        "stories": stories,
        "posts": posts,
        "suggestions": suggestions,
        "highlights": highlights,
        "profile_posts": profile_posts,
        "search_users": search_users,
    }


def index(request):
    context = {
        **get_sample_data(),
        "active_page": "home",
        "sort_options": [
            {"value": "recent", "label": "최신순"},
            {"value": "likes", "label": "좋아요순"},
            {"value": "comments", "label": "댓글순"},
        ],
    }
    return render(request, "instagram/index.html", context)


def profile(request):
    context = {
        **get_sample_data(),
        "active_page": "profile",
    }
    return render(request, "instagram/profile.html", context)


def user_profile(request, username):
    data = get_sample_data()
    other_user = {
        "username": username,
        "name": username,
        "initial": username[:1].upper(),
        "color": "#d4a777",
        "post_count": 1,
        "followers": 0,
        "following": 1,
        "bio": "소개글이 없습니다.",
        "is_following": False,
    }
    context = {
        **data,
        "active_page": "user_search",
        "other_user": other_user,
        "other_user_posts": [{"id": 1}],
    }
    return render(request, "instagram/user_profile.html", context)


def post_search(request):
    context = {
        **get_sample_data(),
        "active_page": "post_search",
        "query": "좋은 하루",
        "sort_options": [
            {"value": "recent", "label": "최신순"},
            {"value": "likes", "label": "좋아요순"},
            {"value": "comments", "label": "댓글순"},
        ],
    }
    return render(request, "instagram/post_search.html", context)


def user_search(request):
    context = {
        **get_sample_data(),
        "active_page": "user_search",
        "query": "pirouser",
    }
    return render(request, "instagram/user_search.html", context)


def post_create(request):
    context = {
        **get_sample_data(),
        "active_page": "post_create",
        "form_title": "게시글 만들기",
        "submit_label": "공유하기",
        "is_edit": False,
    }
    return render(request, "instagram/post_form.html", context)


def post_edit(request, post_id):
    context = {
        **get_sample_data(),
        "active_page": "post_create",
        "form_title": "게시글 수정",
        "submit_label": "수정하기",
        "is_edit": True,
        "post_id": post_id,
    }
    return render(request, "instagram/post_form.html", context)
