
from django.urls import path, include
from rest_framework import routers
from .views import PostClassificationViewSet, CategoryViewSet, PostViewSet, CommentViewSet, like_post

router = routers.DefaultRouter()
router.register(r'post-classifications', PostClassificationViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:post_id>/like', like_post, name='like_post'),
]
