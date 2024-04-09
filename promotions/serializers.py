from .models import Promotion, PromotionArticle
from rest_framework import serializers


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ["id", "title", "banner_image", "link_path"]


class PromotionArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionArticle
        fields = ["id", "title", "sub_title", "thumbnail_image", "link_path"]