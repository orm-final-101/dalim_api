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
    
class Like(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liked_posts")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="posted_likes")
    is_liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("author", "post")

class Comment(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commented_posts")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="posted_comments")
    contents = models.TextField()
    

class Post(models.Model):
    
    title = models.CharField(max_length=128)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    post_classification = models.ForeignKey(PostClassification, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    contents = models.TextField()
    thumbnail_image = models.ImageField(upload_to="thumbnail_images/%Y/%m/%d/", null=True, default="default_thumbnail_image.jpg")
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Like", related_name="author_posts")
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)