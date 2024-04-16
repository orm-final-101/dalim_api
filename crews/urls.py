"""
crews 앱 URL 패턴 정의

- `/`: 공개된 크루 목록 조회 (PublicCrewViewSet)
- `/top6/`: 상위 6개의 크루를 조회 (PublicCrewViewSet - top6 액션)
- `/manage/`: 크루 관리 (ManagerCrewViewSet)
- `/manage/<crew_id>/members/`: 특정 크루의 멤버 관리 (CrewMemberViewSet)
- `/<crew_id>/reviews/`: 특정 크루의 리뷰 CRUD (CrewReviewViewSet)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = "crews"

router = DefaultRouter()
router.register(r"manage/(?P<crew_id>\d+)/members", views.CrewMemberViewSet, basename="joinedcrew")
router.register(r"(?P<crew_id>\d+)/reviews", views.CrewReviewViewSet, basename="crewreview")
router.register("manage", views.ManagerCrewViewSet, basename="manage_crew")
router.register("", views.PublicCrewViewSet, basename="public_crew")

urlpatterns = [
    path("", include(router.urls)),
    path("top6/", views.PublicCrewViewSet.as_view({"get": "top6"}), name="crew_top6"),
]