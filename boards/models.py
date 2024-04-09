from django.db import models
from django.conf import settings
from config.constants import CLASSIFICATION_CHOICES, CATEGORY_CHOICES


class PostClassification(models.Model):

    name = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES)

    def __str__(self):
        return self.name

class Category(models.Model):

    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name
    

class Post(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    contents = models.TextField()
    title = models.CharField(max_length=128)
    thumbnail_image = models.ImageField(upload_to="thumbnail_images/%Y/%m/%d/", null=True, blank=True, default="default_thumbnail_image.jpg")
    post_classification = models.ForeignKey(PostClassification, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commented_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    contents = models.TextField()
    
    
class Like(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = "liked_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "author")
