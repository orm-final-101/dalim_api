from rest_framework import serializers
from .models import PostClassification, Category, Post, Comment

class PostClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostClassification
        fields = ["id", "name"] 

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]  

class PostSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author", "contents", "title", "thumbnail_image", "post_classification", "likes", "category", "view_count", "created_at", "updated_at", "comment_count"]

    def get_comment_count(self, obj):
        return Comment.objects.filter(post=obj).count()

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author", "post", "contents"] 