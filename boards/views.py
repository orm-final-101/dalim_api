from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes#,api_view
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from .models import PostClassification, Category, Post, Comment, Like
from .serializers import PostDetailSerializer, PostClassificationSerializer, CategorySerializer, PostSerializer, CommentSerializer


class PostClassificationViewSet(viewsets.ModelViewSet):
    
    queryset = PostClassification.objects.all()
    serializer_class = PostClassificationSerializer

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'results': data
        })

class PostViewSet(viewsets.ModelViewSet):

    serializer_class = PostSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Post.objects.all()

        page = self.request.query_params.get('page', 1)
        size = self.request.query_params.get('size', 20)
        categories = self.request.query_params.get('category')
        post_classification = self.request.query_params.get('post_classification')

        if categories:
            categories = categories.split(',')
            queryset = queryset.filter(category__in=categories)

        if post_classification:
            post_classification = post_classification.split(',')
            queryset = queryset.filter(post_classification__in=post_classification)

        self.paginator.page_size = size

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = PostDetailSerializer(instance, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer



#@api_view(['GET','POST']) 해당 주석 지우면 is_liked = False 으로 변하지 않음, 문의 예정
@permission_classes([AllowAny])
def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = request.user

    if request.method == "POST":
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
                "count": like_count,
                "is_liked": like.is_liked
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({"error": "User is not authenticated"}, status=400)
    else:
        # GET 요청 처리
        like_count = post.posted_likes.filter(is_liked=True).count()
        is_liked = False
        if author.is_authenticated:
            like = Like.objects.filter(author=author, post=post).first()
            if like:
                is_liked = like.is_liked
        
        response_data = {
            "count": like_count,
            "is_liked": is_liked
        }
        return JsonResponse(response_data)
