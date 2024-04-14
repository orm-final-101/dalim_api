from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Race, RaceReview, RaceFavorite
from .serializers import *
from datetime import date


# 대회 목록 조회
@extend_schema(parameters=[
    OpenApiParameter(name="search", description="Search keyword", required=False, type=str),
    OpenApiParameter(name="reg_status", description="접수예정/접수중/접수마감", required=False, type=str),
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


# 대회 상세 조회
@api_view(["GET"])
def race_detail(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    serializer = RaceDetailSerializer(race,context={"request": request})
    return Response(serializer.data)


# 대회 리뷰 목록조회 및 리뷰 신규작성 
@extend_schema(
    methods=["POST"],
    request=RaceReviewCreateSerializer,
    responses={201: RaceReviewCreateSerializer},
    description="Create a Review for a Race",
    parameters=[
        OpenApiParameter(name="1",description='ID of the Race to review', required=True, type=int)
    ],
    examples=[
        OpenApiExample(
            name="Example response",
            value={
                "author": 1,
                "race": 1,
                "contents": "Review content here."
                
            },
            request_only=True,   
        )
    ]
)
@api_view(["GET", "POST"])  
def race_reviews(request, race_id):
    race = get_object_or_404(Race, id=race_id)

    if request.method == "GET":
        reviews = RaceReview.objects.filter(race=race)
        serializer = RaceReviewListSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if request.user.is_authenticated:
            serializer = RaceReviewCreateSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save(author=request.user, race=race)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)


# 대회 리뷰 수정 및 삭제 
@extend_schema(
    methods=["PATCH"],
    request=RaceReviewUpdateSerializer,
    responses={201: RaceReviewUpdateSerializer},
    description="대회 리뷰 수정",
    parameters=[
        OpenApiParameter(name="사용자명?",description=' 리뷰 ID', required=True, type=int)
    ],
    examples=[
        OpenApiExample(
            name="사용자명?",
            value={
                "author": 1,
                "race": 1,
                "contents": "리뷰 내용 수정"
                
            },
            request_only=True,   
        )
    ]
)
@api_view(["PATCH", "DELETE"])  
@permission_classes([IsAuthenticated])
def race_review_update(request, race_id, review_id):   
    race = get_object_or_404(Race, id=race_id)
    review = get_object_or_404(RaceReview, id=review_id, race=race_id)

    if request.user != review.author:
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method in ["PATCH"]:
        serializer = RaceReviewUpdateSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Top6 접수중 대회 목록 조회
@api_view(['GET'])
def race_top6(request):
    today = date.today()
    
    open_races = Race.objects.filter(reg_start_date__lte=today, reg_end_date__gte=today) 
    sorted_races = sorted(open_races, key=lambda x: x.d_day(), reverse=False)[:6]
    serializer = RaceListSerializer(sorted_races, many=True, context={'request': request})
    return Response(serializer.data)


# Favorite toggle 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def race_favorite(request, race_id):
    user = request.user

    if RaceFavorite.objects.filter(user=user, race=race_id).exists():
        RaceFavorite.objects.filter(user=user, race=race_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        RaceFavorite.objects.create(user=user, race_id=race_id)
        return Response(status=status.HTTP_201_CREATED)

