from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, status
from .models import PostClassification, Category, Post, Comment, Like
from .serializers import PostClassificationSerializer, CategorySerializer, PostListSerializer, LikeSerializer, PostDetailSerializer
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter


class PostClassificationViewSet(viewsets.ModelViewSet):
    
    queryset = PostClassification.objects.all()
    serializer_class = PostClassificationSerializer

class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# 게시판 전체 보기 및 쿼리스트링
@extend_schema(parameters=[
    OpenApiParameter(name='page', description='x번째 페이지', type=int),
    OpenApiParameter(name='size', description='x번째 페이지에 게시물 y개', type=int),
    OpenApiParameter(name='category', description='게시물 성격', type=str),
    OpenApiParameter(name='post_classification', description='게시물 분류', type=str),
])
@api_view(["GET"])
def post_list(request):
    posts = Post.objects.all()
    search_keyword = request.GET.get("search", "")
    selected_category = request.GET.get("category", "")
    selected_post_classification = request.GET.get("post_classification", "")

    if search_keyword:
        posts = posts.filter(
            Q(title__icontains=search_keyword) |
            Q(content__icontains=search_keyword) | 
            Q(category__name__icontains=search_keyword) |
            Q(author__username__icontains=search_keyword) |
            Q(post_classification__name__icontains=search_keyword)
        )

    if selected_category:
        category = Category.objects.filter(name=selected_category).first()
        if category:
            posts = posts.filter(category=category)

    if selected_post_classification:
        post_classification = PostClassification.objects.filter(name=selected_post_classification).first()
        if post_classification:
            posts = posts.filter(post_classification=post_classification)

    paginator = PageNumberPagination()
    page_size = request.GET.get("size", 10)
    paginator.page_size = page_size
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostListSerializer(result_page, many=True, context={"request": request})

    return Response({
        "count": paginator.page.paginator.count,
        "results": serializer.data
    }, status=200)


# 게시판 상세보기
@api_view(['GET'])
def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(status=404)

    serializer = PostDetailSerializer(post, context={'request': request})
    return Response(serializer.data)

# # 게시판 수정하기 
# def update(self, request, *args, **kwargs):
#     partial = kwargs.pop("partial", False)
#     instance = self.get_object()
#     serializer = PostUpdateSerializer(instance, data=request.data, partial=partial)
#     serializer.is_valid(raise_exception=True)
#     self.perform_update(serializer)

#     if getattr(instance, "_prefetched_objects_cache", None):
#         instance._prefetched_objects_cache = {}

#     response_serializer = PostDetailSerializer(instance, context={"request": request})
#     return Response(response_serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
# class CommentViewSet(viewsets.ModelViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer


# @api_view(['GET','POST'])
# @permission_classes([AllowAny])
# def like_post(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     author = request.user

#     if request.method == "POST":
#         if author.is_authenticated:
#             like, created = Like.objects.get_or_create(author=author, post=post)
            
#             if created:
#                 # 좋아요 생성
#                 like.is_liked = True
#                 like.save()
#             else:
#                 # 좋아요 취소
#                 like.is_liked = not like.is_liked
#                 like.save()
            
#             like_count = post.posted_likes.filter(is_liked=True).count()
#             response_data = {
#                 "count": like_count,
#                 "is_liked": like.is_liked
#             }
#             return JsonResponse(response_data)
#         else:
#             return JsonResponse({"error": "User is not authenticated"}, status=400)
#     else:
#         # GET 요청 처리
#         like_count = post.posted_likes.filter(is_liked=True).count()
#         is_liked = False
#         if author.is_authenticated:
#             like = Like.objects.filter(author=author, post=post).first()
#             if like:
#                 is_liked = like.is_liked
        
#         response_data = {
#             "count": like_count,
#             "is_liked": is_liked
#         }
#         return JsonResponse(response_data)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = request.user

    if request.method == "POST":
        if not author.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=400)

        like, created = Like.objects.get_or_create(author=author, post=post)
        like.is_liked = not like.is_liked if not created else True
        like.save()
        serializer = LikeSerializer(like, context={'request': request})
        return JsonResponse(serializer.data)
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