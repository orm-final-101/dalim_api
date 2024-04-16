from config.constants import CLASSIFICATION_CHOICES, CATEGORY_CHOICES
from .models import Post, Like, Comment
from .serializers import CommentSerializer, PostUpdateSerializer, PostListSerializer, PostDetailSerializer, PostCreateSerializer
from .permissions import IsAuthorOrReadOnly, IsStaffOrGeneralClassification
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter


# Pagination
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"
    max_page_size = 1000
    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "results": data
        })


# Post
@extend_schema_view(
        list=extend_schema(
            parameters=[
                OpenApiParameter(name='page', description='x번째 페이지', type=int),
                OpenApiParameter(name='size', description='x번째 페이지에 게시물 y개', type=int),
                OpenApiParameter(name='category', description='게시물 성격', type=str),
                OpenApiParameter(name='post_classification', description='게시물 분류', type=str),
            ]
        )
    )
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthorOrReadOnly ,IsStaffOrGeneralClassification]


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def list(self, request):
        queryset = super().get_queryset()
        search_keyword = self.request.GET.get("search", "")
        selected_category = self.request.GET.get("category", "")
        selected_post_classification = self.request.GET.get("post_classification", "")
        
        if search_keyword:
            queryset = queryset.filter(
                Q(title__icontains=search_keyword) &
                Q(contents__icontains=search_keyword) &
                Q(author__nickname__icontains=search_keyword)
            )

        if selected_category:
            queryset = queryset.filter(category=selected_category)

        if selected_post_classification:
            queryset = queryset.filter(post_classification=selected_post_classification)

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    def get_serializer_class(self):
        if self.action in ["create"]:
            return PostCreateSerializer
        elif self.action in ["retrieve"]:
            return PostDetailSerializer
        elif self.action in ["update", "partial_update"]:
            return PostUpdateSerializer
        return super().get_serializer_class()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        delete_message = serializer.get_delete_message(instance)
        self.perform_destroy(instance)
        return Response({"message": delete_message}, status=status.HTTP_200_OK)


# LIKE API
@api_view(["GET", "POST"])
def like_post(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    author = request.user

    if request.method == "POST":
        if not author.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=400)

        like, created = Like.objects.get_or_create(author=author, post=post)
        if not created:
            like.delete()
        
        like_count = Like.objects.filter(post=post).count()
        is_liked = Like.objects.filter(author=author, post=post).exists()
        
        response_data = {
            "count": like_count,
            "is_liked": is_liked
        }
        return JsonResponse(response_data)
    else:
        # GET 요청 처리
        like_count = Like.objects.filter(post=post).count()
        is_liked = False
        if author.is_authenticated:
            is_liked = Like.objects.filter(author=author, post=post).exists()
        response_data = {
            "count": like_count,
            "is_liked": is_liked
        }
        return JsonResponse(response_data)
    
    
# Category, post_classification API
@api_view(["GET"])
def get_category_choices(request):
    post_classification_choices = [
        {"value": choice[0], "label": choice[1]}
        for choice in CLASSIFICATION_CHOICES
    ]
    category_choices = [
        {"value": choice[0], "label": choice[1]}
        for choice in CATEGORY_CHOICES
    ]

    data = {
        "post_classification": post_classification_choices,
        "category": category_choices
    }

    return Response(data)


# comment
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post_id=post_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "댓글을 삭제했습니다"}, status=status.HTTP_200_OK)