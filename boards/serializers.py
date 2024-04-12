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
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author_id', 'author_nickname', 'title', 'thumbnail_image',
            'post_classification', 'category', 'view_count', 'comment_count',
            'created_at', 'updated_at', 'is_liked', 'like_count'
        ]

    def get_comment_count(self, obj):
        return obj.posted_comments.count()

    def get_like_count(self, obj):
        return Like.objects.filter(post=obj, is_liked=True).count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Like.objects.filter(author=user, post=obj, is_liked=True).exists()
        return False

class LikeSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ['id', 'author', 'post', 'is_liked', 'created_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.posted_likes.filter(author=request.user, is_liked=True).exists()
        return False

    def get_like_count(self, obj):
        # 여기서는 obj가 Like 모델의 인스턴스일 것으로 가정합니다.
        # 만약 Like 모델이 아니라 다른 모델(Post 등)의 인스턴스가 필요하다면,
        # 해당 인스턴스를 어떻게 참조할지에 대한 추가 정보가 필요합니다.
        return obj.posted_likes.filter(is_liked=True).count()

class PostDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'
    )
    post_classification = serializers.SlugRelatedField(
        queryset=PostClassification.objects.all(),
        slug_field='name'
    )
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            like = Like.objects.filter(post=obj, author=user).first()
            return {
                "count": obj.likes.count(),
                "is_liked": like.is_liked if like else False
            }
        return {
            "count": obj.likes.count(),
            "is_liked": False
        }

    class Meta:
        model = Post
        fields = ['id', 'author_id', 'author_nickname', 'title', 'contents', 'thumbnail_image', 'post_classification', 'category', 'view_count', 'created_at', 'updated_at', 'likes']

    def retrieve(self, instance):
        instance.view_count += 1
        instance.save()
        return instance


class PostUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'
    )
    post_classification = serializers.SlugRelatedField(
        queryset=PostClassification.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = Post
        fields = ['title', 'contents', 'thumbnail_image', 'post_classification', 'category']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.contents = validated_data.get('contents', instance.contents)
        instance.thumbnail_image = validated_data.get('thumbnail_image', instance.thumbnail_image)
        instance.post_classification = validated_data.get('post_classification', instance.post_classification)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance


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