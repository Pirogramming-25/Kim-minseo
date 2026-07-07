from django.urls import path

from . import views

app_name = "instagram"

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),
    path("profile/avatar/", views.profile_avatar_update, name="profile_avatar_update"),
    path("users/<str:username>/", views.user_profile, name="user_profile"),
    path("search/posts/", views.post_search, name="post_search"),
    path("search/users/", views.user_search, name="user_search"),
    path("posts/create/", views.post_create, name="post_create"),
    path("posts/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("posts/<int:post_id>/like/", views.post_like, name="post_like"),
    path("posts/<int:post_id>/save/", views.post_save, name="post_save"),
    path("posts/<int:post_id>/comments/", views.comment_create, name="comment_create"),
    path("stories/create/", views.story_create, name="story_create"),
    path("comments/<int:comment_id>/edit/", views.comment_update, name="comment_update"),
    path("comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
    path("users/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
]
