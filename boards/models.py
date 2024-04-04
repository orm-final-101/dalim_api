from django.db import models
from django.conf import settings


class PostClassification(models.Model):

    CLASSIFICATION_CHOICES = [
        ("general", "일반"),
        ("event", "이벤트"),
        ("announcement", "공지"),
    ]

    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES)

    def __str__(self):
        return self.get_classification_display()
    

class Category(models.Model):

    CATEGORY_CHOICES = [
        ("general", "일반"),
        ("training", "훈련"),
        ("running_gear", "러닝용품"),
        ("end_of_month_sale", "월말결산"),
        ("course_recommendation", "코스추천"),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.get_category_display()
    

class Post(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    contents = models.TextField()
    title = models.CharField(max_length=128)
    thumbnail_image = models.ImageField(upload_to="thumbnail_images/%Y/%m/%d/", null=True, blank=True, default="default_thumbnail_image.jpg") # 이미지 높이, 너비 조율필요
    post_classifications = models.ForeignKey(PostClassification, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commented_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    contents = models.TextField()
    
    
class Like(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = "liked_posts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "author")