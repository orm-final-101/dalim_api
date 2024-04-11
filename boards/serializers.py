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
# 게시물 상세보기
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


class PostCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'
    )
    post_classification = serializers.SlugRelatedField(
        queryset=PostClassification.objects.all(),
        slug_field='name'
    )
    thumbnail_image = serializers.ImageField(required=False)
    class Meta:
        model = Post
        fields = ['author', 'title', 'contents', 'category', 'post_classification', 'thumbnail_image']

    def validate_category(self, value):
        try:
            category = Category.objects.get(name=value)
            return category
        except Category.DoesNotExist:
            raise serializers.ValidationError("Invalid category.")

    def validate_post_classification(self, value):
        try:
            post_classification = PostClassification.objects.get(name=value)
            return post_classification
        except PostClassification.DoesNotExist:
            raise serializers.ValidationError("Invalid post classification.")

    def validate(self, attrs):
        thumbnail_image = attrs.get('thumbnail_image')
        if not thumbnail_image:
            raise serializers.ValidationError("Thumbnail image is required.")

        return attrs

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        return post
    

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