from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class DevTool(models.Model):
    name = models.CharField("이름", max_length=100, unique=True)
    kind = models.CharField("종류", max_length=100)
    content = models.TextField("설명")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("ideas:devtool_detail", kwargs={"pk": self.pk})


class Idea(models.Model):
    title = models.CharField("제목", max_length=120)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="작성자",
        related_name="ideas",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    image = models.ImageField("이미지", upload_to="ideas/", blank=True)
    content = models.TextField("내용")
    interest = models.PositiveIntegerField("관심도", default=0, validators=[MinValueValidator(0)])
    devtools = models.ManyToManyField(
        DevTool,
        verbose_name="개발툴",
        related_name="ideas",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("ideas:idea_detail", kwargs={"pk": self.pk})


class IdeaStar(models.Model):
    idea = models.ForeignKey(Idea, related_name="stars", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="idea_stars",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["idea", "session_key"],
                name="unique_idea_star_per_session",
            ),
            models.UniqueConstraint(
                fields=["idea", "user"],
                name="unique_idea_star_per_user",
            )
        ]

    def __str__(self):
        return f"{self.idea} star"
