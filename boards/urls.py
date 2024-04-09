python


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DefaultRouter 인스턴스 생성
router = DefaultRouter()

# router에 ViewSet 등록
router.register(r'postclassifications', views.PostClassificationViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'likes', views.LikeViewSet)

# URLConf
urlpatterns = [
    path('', include(router.urls)),
]