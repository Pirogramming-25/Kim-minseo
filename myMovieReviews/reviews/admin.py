from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year", "genre", "rating", "director")
    list_filter = ("genre", "release_year")
    search_fields = ("title", "director", "actor")
