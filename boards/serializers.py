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


# 유저 오픈프로필에서 내가 작성한 덧글 볼 때 사용
class ProfileCommentSerializer(serializers.ModelSerializer):
    post = serializers.SerializerMethodField()
    comment = serializers.CharField(source="contents")

    def get_post(self, obj):
        return {
            "id": obj.post.id,
            "title": obj.post.title,
            "author": obj.post.author.nickname
        }
    class Meta:
        model = Comment
        fields = ["post", "comment"]


# 유저 오픈프로필에서 내가 좋아한 게시글 볼 때 사용
class ProfileLikedPostSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(source="post.id")
    title = serializers.CharField(source="post.title")
    author = serializers.CharField(source="post.author.nickname")
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        return Comment.objects.filter(post=obj.post).count()
    
    def get_like_count(self, obj):
        return obj.post.likes.count()
    class Meta:
        model = Post
        fields = ["post_id", "title", "author", "comment_count", "like_count"]