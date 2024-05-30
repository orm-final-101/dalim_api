from django.contrib import admin
from .models import Post, Comment, Like


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


class LikeInline(admin.TabularInline):
    model = Like
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [LikeInline, CommentInline]
    list_display = (
        "title",
        "author",
        "post_classification",
        "category",
        "created_at",
        "updated_at",
    )
    list_filter = ("post_classification", "category", "created_at", "updated_at")
    search_fields = ("title", "author__username", "contents")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "contents")
    list_filter = ("post__title", "author")
    search_fields = ("contents",)
