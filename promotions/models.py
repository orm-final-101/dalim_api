from django.db import models


class Promotion(models.Model):
    title = models.CharField(max_length=100) # 프로모션 제목. alt로 들어감
    banner_image = models.ImageField(upload_to="promotion/banners/%Y/%m/%d/", null=True)
    link_path = models.TextField() # crew/1 형식으로 프론트 path 들어감
    is_show = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PromotionArticle(models.Model):
    title = models.CharField(max_length=100) # 프로모션 제목. alt로 들어감
    sub_title = models.CharField(max_length=100) # 프로모션 소제목. 윗줄에 작게 들어감
    thumbnail_image = models.ImageField(upload_to="promotion/article_thumbnails/%Y/%m/%d/", null=True)
    link_path = models.TextField() # board/1 형식으로 프론트 path 들어감
    is_show = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title