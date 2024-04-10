from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = "crews"

router = DefaultRouter()
router.register("crews", views.PublicCrewViewSet, basename="public_crew")
router.register("manage/crews", views.ManagerCrewViewSet, basename="manage_crew")
router.register("crews/(?P<crew_id>\\d+)/reviews", views.CrewReviewViewSet, basename="crewreview")
router.register("manage/crews/(?P<crew_id>\\d+)/members", views.CrewMemberViewSet, basename="joinedcrew")

urlpatterns = [
    path("", include(router.urls)),
    path("crews/popular/", views.PublicCrewViewSet.as_view({"get": "popular"}), name="crew-popular"),
]