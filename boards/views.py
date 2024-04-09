from rest_framework import viewsets
from .models import PostClassification, Category, Post, Comment, Like
from .serializers import PostClassificationSerializer, CategorySerializer, PostSerializer, CommentSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view

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



@api_view(['GET','POST'])
@permission_classes([AllowAny]) # 접근 권한 누구나 
def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = request.user

    if request.method == 'POST':
        if author.is_authenticated:
            like, created = Like.objects.get_or_create(author=author, post=post)
            
            if created:
                # 좋아요 생성
                like.is_liked = True
                like.save()
            else:
                # 좋아요 취소
                like.is_liked = not like.is_liked
                like.save()
            
            like_count = post.posted_likes.filter(is_liked=True).count()
            response_data = {
                'count': like_count,
                'is_liked': like.is_liked
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'User is not authenticated'}, status=400)
    else:
        # GET 요청 처리
        like_count = post.posted_likes.filter(is_liked=True).count()
        is_liked = False
        if author.is_authenticated:
            like = Like.objects.filter(author=author, post=post).first()
            if like:
                is_liked = like.is_liked
        
        response_data = {
            'count': like_count,
            'is_liked': is_liked
        }
        return JsonResponse(response_data)
