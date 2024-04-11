from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = "crews"

router = DefaultRouter()
router.register("", views.PublicCrewViewSet, basename="public_crew")
router.register("manage/", views.ManagerCrewViewSet, basename="manage_crew")
router.register("(?P<crew_id>\\d+)/reviews/", views.CrewReviewViewSet, basename="crewreview")
router.register("manage/(?P<crew_id>\\d+)/members/", views.CrewMemberViewSet, basename="joinedcrew")

urlpatterns = [
    path("", include(router.urls)),
    path("top6/", views.PublicCrewViewSet.as_view({"get": "top6"}), name="crew-top6"),
]