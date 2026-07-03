from django.contrib import admin

from .models import DevTool, Idea, IdeaStar


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "devtool", "interest", "created_at")
    list_filter = ("devtool", "author")
    search_fields = ("title", "content", "devtool__name", "author__username")


@admin.register(DevTool)
class DevToolAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "created_at")
    search_fields = ("name", "kind", "content")


@admin.register(IdeaStar)
class IdeaStarAdmin(admin.ModelAdmin):
    list_display = ("idea", "user", "session_key", "created_at")
    search_fields = ("idea__title", "user__username", "session_key")
