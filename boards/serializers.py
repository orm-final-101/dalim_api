from rest_framework import serializers
from .models import PostClassification, Category, Post, Comment


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


# 전체 보기를 위한 serializers.py
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


class PostDetailSerializer(serializers.ModelSerializer):
    author_nickname = serializers.ReadOnlyField(source="author.nickname")
    thumbnail_image = serializers.ImageField()
    post_classification = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author_id", "author_nickname", "title", "contents", "thumbnail_image", "post_classification", "category", "view_count", "created_at", "updated_at", "likes"]

    def get_likes(self, obj):
        likes_count = obj.posted_likes.count()
        is_liked = False
        if self.context["request"].user.is_authenticated:
            is_liked = obj.posted_likes.filter(author=self.context["request"].user, is_liked=True).exists()
        return {"count": likes_count, "is_liked": is_liked}


class PostUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = Post
        fields = ["title", "contents", "thumbnail_image", "category"]