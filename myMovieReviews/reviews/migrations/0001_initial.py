import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="영화 제목")),
                (
                    "release_year",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1888),
                            django.core.validators.MaxValueValidator(2100),
                        ],
                        verbose_name="개봉 년도",
                    ),
                ),
                (
                    "genre",
                    models.CharField(
                        choices=[
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
                        ],
                        max_length=20,
                        verbose_name="장르",
                    ),
                ),
                (
                    "rating",
                    models.DecimalField(
                        decimal_places=1,
                        max_digits=2,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="별점",
                    ),
                ),
                ("running_time", models.PositiveIntegerField(verbose_name="러닝타임")),
                ("review", models.TextField(verbose_name="리뷰 내용")),
                ("director", models.CharField(max_length=100, verbose_name="감독")),
                ("actor", models.CharField(max_length=150, verbose_name="주연")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"],},
        ),
    ]
