from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register("", views.RecordViewSet, basename='record')

urlpatterns = [
    path("signup/", include("dj_rest_auth.registration.urls")),
    path("login/", LoginView.as_view(), name="account_login"),
    path("logout/", LogoutView.as_view(), name="account_logout"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("mypage/info/", views.mypage_info),
    path("mypage/record/", include(router.urls)),
]