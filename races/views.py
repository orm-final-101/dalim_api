from django.db.models import Count, Q
from accounts.models import JoinedCrew
from .models import Race, RaceReview, RaceFavorite
from rest_framework import status
from rest_framework.decorators import api_view #, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from .permissions import IsCrewOwner, IsCrewAdmin, IsCrewMemberOrQuit
from .serializers import RaceListSerializer, RaceDetailSerializer, RaceReviewListSerializer, RaceReviewDetailSerializer, JoinedRaceSerializer
from config.constants import COURSE_CHOICES
# from django.shortcuts import get_object_or_404


# 대회 목록 조회
@api_view(["GET"])
def get_race_list(request):
    races = Race.objects.all()
    search_keyword = request.GET.get("search", "")
    search_race_status = request.GET.get("search", "")
    
    if search_keyword:
        races = races.filter(
            Q(title__icontains=search_keyword) |
            Q(description__icontains=search_keyword)
        )
        

    if selected_courses:
        selected_courses = [course[0] for course in COURSE_CHOICES if course[0] in COURSE_CHOICES]
        for course in COURSE_CHOICES:
            courses = courses.filter(COURSE_CHOICES=course)

    serializer = RacesListSerializer(races, many=True, context={"request": request})
    return Response(serializer.data)
