from django.contrib import admin
from .models import Post, PostClassification, Category, Comment, Like

@admin.register(PostClassification)
class PostClassificationAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "post_classification", "category", "created_at", "updated_at")
    list_filter = ("post_classification", "category", "created_at", "updated_at")
    search_fields = ("title", "author__username", "contents")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "contents")
    list_filter = ("post__title", "author")
    search_fields = ("contents",)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "created_at")
    list_filter = ("post__title", "author")