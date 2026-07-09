from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    color = models.CharField(max_length=20, default="#d4a5a5")

    def __str__(self):
        return self.user.username

    @property
    def initial(self):
        return (self.display_name or self.user.username)[:1].upper()


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_relations")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_relations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follow"),
            models.CheckConstraint(check=~models.Q(follower=models.F("following")), name="prevent_self_follow"),
        ]

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    caption = models.TextField()
    location = models.CharField(max_length=80, blank=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    saved_by = models.ManyToManyField(User, related_name="saved_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username}: {self.caption[:20]}"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/")

    def __str__(self):
        return f"post image {self.post_id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=300)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="replies", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}"


class Story(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "stories"

    def __str__(self):
        return f"{self.author.username}'s story"


class StoryImage(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="stories/", blank=True, null=True)
    color = models.CharField(max_length=20, default="#9fd3ca")

    def __str__(self):
        return f"story image {self.story_id}"
