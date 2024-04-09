from rest_framework import serializers
from .models import PostClassification, Category, Post, Comment, Like

class PostClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostClassification
        fields = ["id", "classification"] 

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category"]  

class PostSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author", "contents", "title", "thumbnail_image", "post_classification", "category", "view_count", "created_at", "updated_at", "comment_count"]

    def get_comment_count(self, obj):
        return Comment.objects.filter(post=obj).count()

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author", "post", "contents"]  

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "author", "post", "created_at"]