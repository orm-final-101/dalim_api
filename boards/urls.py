from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import post_list, PostClassificationViewSet, CategoryViewSet, like_post, post_detail

router = DefaultRouter()
router.register(r'post-classifications', PostClassificationViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', post_list, name='post_list'),
    path('<int:post_id>/', post_detail, name='post_detail'),
    path('<int:post_id>/like/', like_post, name='like_post'),
    path('', include(router.urls)),
    
]