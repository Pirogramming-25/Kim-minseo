from django.contrib import admin

from .models import Comment, Follow, Post, PostImage, Profile, Story, StoryImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


class StoryImageInline(admin.TabularInline):
    model = StoryImage
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "caption", "created_at")
    filter_horizontal = ("likes", "saved_by")
    inlines = [PostImageInline]


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at")
    inlines = [StoryImageInline]


admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(PostImage)
admin.site.register(StoryImage)
