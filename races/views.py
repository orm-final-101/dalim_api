# from django.db.models import Count, Q
# from accounts.models import JoinedCrew
# from .models import Race, RaceReview, RaceFavorite
# from rest_framework import status
# from rest_framework.decorators import api_view #, permission_classes
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# # from .permissions import IsCrewOwner, IsCrewAdmin, IsCrewMemberOrQuit
# from .serializers import RaceListSerializer

# # from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from django.db.models import Q
from .serializers import RaceListSerializer
from .models import Race 
from datetime import date


# 대회 목록 조회
@extend_schema(parameters=[
    OpenApiParameter(name='search', description='Search keyword', required=False, type=str),
    OpenApiParameter(name='reg_status', description='접수예정/접수중/접수마감', required=False, type=str),
])
@api_view(["GET"])
def race_list(request):
    races = Race.objects.all()
    
    search_keyword = request.GET.get("search", "")
    if search_keyword:
        races = races.filter(
            Q(title__icontains=search_keyword) |
            Q(description__icontains=search_keyword)
        )

    search_reg_status = request.GET.get("reg_status", "")
    today = date.today()
    if search_reg_status == "접수예정":
        races = races.filter(reg_start_date__gt=today)
    elif search_reg_status == "접수중":
        races = races.filter(reg_start_date__lte=today, reg_end_date__gte=today)
    elif search_reg_status == "접수마감":
        races = races.filter(reg_end_date__lt=today)


    serializer = RaceListSerializer(races, many=True, context={"request": request})
    return Response(serializer.data)