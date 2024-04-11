from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import like_post, post_detail, PostViewSet

router = DefaultRouter()
router.register(r'', PostViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('<int:post_id>/', post_detail, name='post_detail'),
    path('<int:post_id>/like/', like_post, name='like_post'),
]