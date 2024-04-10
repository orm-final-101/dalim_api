from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostClassificationViewSet, CategoryViewSet, PostViewSet, CommentViewSet, like_post

router = DefaultRouter()
router.register(r'post-classifications', PostClassificationViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_id>/like', like_post, name='like_post'),
]