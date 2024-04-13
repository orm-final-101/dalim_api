from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import like_post, PostViewSet, get_category_choices

# router 객체 생성
router = DefaultRouter()

# PostViewSet을 '/boards' URL 패턴에 등록
router.register(r'', PostViewSet)

# urlpatterns 설정
urlpatterns = [
    # router에 등록된 URL 패턴을 include
    path('', include(router.urls)),
    # 좋아요 기능을 위한 URL 패턴
    path('<int:post_id>/like', like_post, name='like_post'),
    path('category', get_category_choices, name='category_choices')
]