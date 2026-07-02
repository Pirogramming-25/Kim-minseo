from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Review(models.Model):
    GENRE_CHOICES = [
        ("Action", "Action"),
        ("Comedy", "Comedy"),
        ("Drama", "Drama"),
        ("Fantasy", "Fantasy"),
        ("Horror", "Horror"),
        ("Romance", "Romance"),
        ("SF", "SF"),
        ("Thriller", "Thriller"),
        ("Animation", "Animation"),
        ("Documentary", "Documentary"),
    ]

    title = models.CharField("영화 제목", max_length=100)
    release_year = models.PositiveIntegerField(
        "개봉 년도",
        validators=[MinValueValidator(1888), MaxValueValidator(2100)],
    )
    genre = models.CharField("장르", max_length=20, choices=GENRE_CHOICES)
    rating = models.DecimalField(
        "별점",
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    running_time = models.PositiveIntegerField("러닝타임")
    poster = models.FileField("포스터", upload_to="posters/", blank=True)
    review = models.TextField("리뷰 내용")
    director = models.CharField("감독", max_length=100)
    actor = models.CharField("주연", max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("reviews:detail", kwargs={"pk": self.pk})

    @property
    def running_time_display(self):
        hours = self.running_time // 60
        minutes = self.running_time % 60
        if hours and minutes:
            return f"{hours}시간 {minutes}분"
        if hours:
            return f"{hours}시간"
        return f"{minutes}분"
