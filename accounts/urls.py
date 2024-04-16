from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.views import LoginView, LogoutView
from . import views


app_name = "accounts"

router = DefaultRouter()
router.register("mypage/record", views.RecordViewSet, basename="record")
router.register("mypage/race", views.RaceViewSet, basename="joined_race")
router.register("mypage/info", views.UserInfoViewSet, basename="info")
router.register("mypage/crew", views.MypageCrewViewSet, basename="mypage_crew")
router.register("mypage/favorites", views.MypageFavoritesViewSet, basename="mypage_favorite")
router.register("profile", views.ProfileViewSet, basename="profile")


urlpatterns = [
    path("", include(router.urls)),
    path("login/", LoginView.as_view(), name="account_login"),
    path("logout/", LogoutView.as_view(), name="account_logout"),
    path("signup/", views.CustomRegisterView.as_view(), name="account_signup"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]