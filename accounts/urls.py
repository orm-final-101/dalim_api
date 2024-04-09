from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.views import LoginView, LogoutView
from . import views


record_router = DefaultRouter()
record_router.register("", views.RecordViewSet, basename="record")

race_router = DefaultRouter()
race_router.register("", views.RaceViewSet, basename="joined_race")

urlpatterns = [
    path("signup/", include("dj_rest_auth.registration.urls")),
    path("login/", LoginView.as_view(), name="account_login"),
    path("logout/", LogoutView.as_view(), name="account_logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("mypage/info/", views.mypage_info),
    path("mypage/crew/", views.mypage_crew),
    path("mypage/record/", include(record_router.urls)),
    path("mypage/race/", include(race_router.urls)),
]