from rest_framework import viewsets
from .models import PostClassification, Category, Post, Comment, Like
from .serializers import PostClassificationSerializer, CategorySerializer, PostSerializer, CommentSerializer, LikeSerializer

class PostClassificationViewSet(viewsets.ModelViewSet):
    queryset = PostClassification.objects.all()
    serializer_class = PostClassificationSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer