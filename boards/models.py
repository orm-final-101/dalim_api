from django.db import models
from django.conf import settings
from config.constants import CLASSIFICATION_CHOICES, CATEGORY_CHOICES


# 좋아요
class Like(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liked_posts"
    )
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="posted_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("author", "post")


# 댓글
class Comment(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commented_posts",
    )
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="posted_comments"
    )
    contents = models.TextField()


# 게시물
class Post(models.Model):

    title = models.CharField(max_length=128)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    post_classification = models.CharField(
        max_length=20, choices=CLASSIFICATION_CHOICES
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    contents = models.TextField()
    thumbnail_image = models.ImageField(
        upload_to="thumbnail_images/%Y/%m/%d/", null=True
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Like", related_name="author_posts"
    )
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
