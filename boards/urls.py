from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import post_list, PostClassificationViewSet, CategoryViewSet, CommentViewSet, like_post

router = DefaultRouter()
router.register(r'post-classifications', PostClassificationViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', post_list, name='post_list'),
    path('', include(router.urls)),
    path('<int:pk>/like/', like_post, name='like_post'),
    
]