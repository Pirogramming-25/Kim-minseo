from django.urls import path

from . import views

app_name = "instagram"

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),
    path("users/<str:username>/", views.user_profile, name="user_profile"),
    path("search/posts/", views.post_search, name="post_search"),
    path("search/users/", views.user_search, name="user_search"),
    path("posts/create/", views.post_create, name="post_create"),
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
]
