from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCrewOwner, IsCrewAdmin, IsCrewMemberOrQuit
from django.shortcuts import get_object_or_404
from .models import Crew, CrewReview, CrewFavorite
from .serializers import CrewListSerializer, CrewDetailSerializer, CrewReviewListSerializer, CrewReviewCreateSerializer, CrewReviewUpdateSerializer, CrewCreateSerializer, JoinedCrewSerializer
from accounts.models import JoinedCrew


# 크루 리스트
@api_view(["GET"])
def crew_list(request):
    crews = Crew.objects.all()
    
    search_keyword = request.GET.get("search", "")
    if search_keyword:
        crews = crews.filter(name__icontains=search_keyword)
    
    serializer = CrewListSerializer(crews, many=True, context={"request": request})
    return Response(serializer.data)


# 크루 상세
@api_view(["GET"])
def crew_detail(request, crew_id):
    crew = Crew.objects.get(pk=crew_id)
    serializer = CrewDetailSerializer(crew, context={"request": request})
    return Response(serializer.data)


# 크루 가입
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crew_join(request, crew_id):
    crew = Crew.objects.get(pk=crew_id)
    user = request.user
    
    if JoinedCrew.objects.filter(user=user, crew=crew).exists():
        joined_crew = JoinedCrew.objects.get(user=user, crew=crew)
        
        if joined_crew.status == "member":
            return Response({"error": "이미 회원입니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif joined_crew.status == "non_keeping":
            return Response({"error": "신청할 수 없는 크루입니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif joined_crew.status == "keeping":
            return Response({"error": "이미 신청한 크루입니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    JoinedCrew.objects.create(user=user, crew=crew, status="keeping")
    return Response({"message": "가입 신청이 완료되었습니다."}, status=status.HTTP_200_OK)


# 크루 즐겨찾기
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crew_favorite(request, crew_id):
    crew = Crew.objects.get(pk=crew_id)
    user = request.user

    if CrewFavorite.objects.filter(user=user, crew=crew).exists():
        CrewFavorite.objects.filter(user=user, crew=crew).delete()
    else:
        CrewFavorite.objects.create(user=user, crew=crew)

    return Response(status=status.HTTP_200_OK)


# 탑6 크루(메인에 활용)
@api_view(["GET"])
def crew_opened_top6(request):
    top6_crews = Crew.objects.filter(is_opened=True).annotate(favorite_count=Count("crewfavorite")).order_by("-favorite_count")[:6]
    serializer = CrewListSerializer(top6_crews, many=True, context={"request": request})
    return Response(serializer.data)


# 크루 리뷰 CRUD
@api_view(["GET", "POST"])
def crew_review_list_create(request, crew_id):
    crew = get_object_or_404(Crew, id=crew_id)

    if request.method == "GET":
        reviews = CrewReview.objects.filter(crew=crew)
        serializer = CrewReviewListSerializer(reviews, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        if not IsCrewMemberOrQuit().has_object_permission(request, crew_review_list_create, crew):
            return Response({"error": "리뷰 작성 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CrewReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, crew=crew)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def crew_review_update_delete(request, crew_id, review_id):
    crew = get_object_or_404(Crew, id=crew_id)
    review = get_object_or_404(CrewReview, id=review_id, crew=crew)

    if request.user != review.author:
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method in ["PUT", "PATCH"]:
        serializer = CrewReviewUpdateSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# (관리자)크루 상세
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCrewOwner])
def manage_crew_detail(request, crew_id):
    crew = Crew.objects.get(pk=crew_id)
    serializer = CrewDetailSerializer(crew, context={"request": request})
    return Response(serializer.data)


# (관리자)크루 생성, 수정
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsCrewAdmin])
def crew_create(request):
    serializer = CrewCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated, IsCrewOwner, IsCrewAdmin])
def crew_update(request, crew_id):
    crew = Crew.objects.get(pk=crew_id)
    serializer = CrewCreateSerializer(crew, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# (관리자)크루 멤버 리스트, 수정
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCrewAdmin])
def crew_member_list(request, crew_id):
    crew_members = JoinedCrew.objects.filter(crew_id=crew_id)
    serializer = JoinedCrewSerializer(crew_members, many=True)
    return Response(serializer.data)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsCrewAdmin])
def crew_member_update(request, crew_id, member_id):
    crew_member = get_object_or_404(JoinedCrew, id=member_id, crew_id=crew_id)
    serializer = JoinedCrewSerializer(crew_member, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)