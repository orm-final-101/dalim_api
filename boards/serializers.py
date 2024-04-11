from rest_framework import serializers
from .models import PostClassification, Category, Post, Comment, Like


class PostClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostClassification
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author", "post", "contents"] 

# 게시물 전체 보기
class PostListSerializer(serializers.ModelSerializer):

    author_nickname = serializers.CharField(source='author.nickname')
    comment_count = serializers.SerializerMethodField()
    post_classification = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = Post
        fields = [
            'id', 'author_id', 'author_nickname', 'title', 'thumbnail_image',
            'post_classification', 'category', 'view_count', 'comment_count',
            'created_at', 'updated_at'
        ]

    def get_comment_count(self, obj):
        return obj.posted_comments.count()


class LikeSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ('count', 'is_liked')

    def get_count(self, obj):
        return obj.post.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        return obj.post.likes.filter(user=request.user).exists()

class PostDetailSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    author_nickname = serializers.CharField(source='author.nickname')
    post_classification = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    class Meta:
        model = Post
        fields = ('id', 'author_id', 'author_nickname', 'title', 'contents', 'thumbnail_image', 'post_classification', 'category', 'view_count', 'created_at', 'updated_at', 'likes')

    def get_likes(self, obj):
        request = self.context.get('request')
        is_liked = obj.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False
        return {
            'count': obj.likes.count(),
            'is_liked': is_liked
        }


class PostSerializer(serializers.ModelSerializer):
    author_nickname = serializers.ReadOnlyField(source="author.nickname")
    thumbnail_image = serializers.ImageField()
    comment_count = serializers.SerializerMethodField()
    post_classification = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = Post
        fields = ["id", "author_id", "author_nickname", "title", "thumbnail_image", "post_classification", "category", "view_count", "comment_count", "created_at", "updated_at"]
        
    def get_comment_count(self, obj):
        return obj.posted_comments.count()


class PostUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = Post
        fields = ["title", "contents", "thumbnail_image", "category"]