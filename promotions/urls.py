from django.urls import path
from . import views

urlpatterns = [
    path("", views.promotion_main, name="promotion_main"),
    path("post/", views.promotion_post, name="promotion_post"),
]