from django.urls import path, include
from . import views

urlpatterns = [
    path("signup/", include("dj_rest_auth.registration.urls")),
    path("", include("dj_rest_auth.urls")),
    # path('mypage/info', views.mypage_info, name='mypage_info'),
    # path('mypage/distance', views.mypage_distance, name='mypage_distance'),
]