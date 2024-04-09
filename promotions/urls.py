from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.PromotionViewSet, basename='promotion')  # URL 패턴을 '/'로 설정합니다.
router.register(r'post', views.PromotionArticleViewSet, basename='promotion_article')  # URL 패턴을 '/post/'로 설정합니다.

urlpatterns = [
    path('', include(router.urls)),
]