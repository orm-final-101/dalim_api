from django.db.models import Q, Count
from accounts.models import JoinedCrew
from .models import Crew, CrewReview, CrewFavorite
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCrewOwner, IsCrewAdmin, IsCrewMemberOrQuit
from .serializers import CrewListSerializer, CrewDetailSerializer, CrewReviewListSerializer, CrewReviewCreateSerializer, CrewReviewUpdateSerializer, CrewCreateSerializer, JoinedCrewSerializer
from config.constants import MEET_DAY_CHOICES, LOCATION_CITY_CHOICES
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
import functools, operator


"""
일반 크루 페이지

- "모집중"인 상태의 크루 리스트
- 검색, 필터링 기능
- 해당 크루의 상세 페이지
- 크루 가입 신청, 즐겨찾기 추가/제거 기능
"""
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(name="search", description="검색 키워드", required=False, type=str),
            OpenApiParameter(name="location_city", description="도시 선택", required=False, type=str),
            OpenApiParameter(name="meet_days", description="요일 선택", required=False, type=str),
        ]
    )
)
# 일반 크루 페이지
class PublicCrewViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CrewListSerializer

    # 모집중인 크루만 조회
    def get_queryset(self):
        if self.action == "list":
            return Crew.objects.filter(is_opened=True)
        return Crew.objects.all()

    # 상세 페이지
    def get_serializer_class(self):
        if self.action == "retrieve":
            return CrewDetailSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # 크루 검색 및 필터링 기능
    def filter_queryset(self, queryset):
        search_keyword = self.request.GET.get("search", "")
        selected_location_city = self.request.GET.get("location_city", "")
        selected_meet_days = self.request.GET.get("meet_days", "")

        # 검색어 필터링
        if search_keyword:
            queryset = queryset.filter(
                Q(name__icontains=search_keyword) |
                Q(description__icontains=search_keyword)
            )

        # 지역 필터링
        if selected_location_city:
            selected_location_city = [city[0] for city in LOCATION_CITY_CHOICES if city[0] == selected_location_city]
            if selected_location_city:
                queryset = queryset.filter(location_city=selected_location_city[0])

        # 요일 필터링
        if selected_meet_days:
            selected_meet_days = selected_meet_days.split(",")
            valid_meet_days = [day[0] for day in MEET_DAY_CHOICES]
            selected_meet_days = [day for day in selected_meet_days if day in valid_meet_days]
            queryset = queryset.filter(
                functools.reduce(operator.and_, (Q(meet_days__contains=day) for day in selected_meet_days))
            )
        return queryset
    
    # 크루 가입 신청 기능
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        crew = self.get_object()
        user = request.user

        if JoinedCrew.objects.filter(user=user, crew=crew).exists():
            joined_crew = JoinedCrew.objects.get(user=user, crew=crew)
            if joined_crew.status == "member":
                return Response({"error": "이미 회원입니다."}, status=status.HTTP_400_BAD_REQUEST)
            elif joined_crew.status == "non_keeping":
                return Response({"error": "신청할 수 없는 크루입니다."}, status=status.HTTP_400_BAD_REQUEST)
            elif joined_crew.status == "quit":
                joined_crew.status = "keeping"
                joined_crew.save()
                return Response({"message": "가입 신청이 완료되었습니다."}, status=status.HTTP_200_OK)
            elif joined_crew.status == "keeping":
                return Response({"error": "이미 신청한 크루입니다."}, status=status.HTTP_400_BAD_REQUEST)

        JoinedCrew.objects.create(user=user, crew=crew, status="keeping")
        return Response({"message": "가입 신청이 완료되었습니다."}, status=status.HTTP_200_OK)

    # 크루 즐겨찾기 추가/제거 기능 
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        crew = self.get_object()
        user = request.user

        if CrewFavorite.objects.filter(user=user, crew=crew).exists():
            CrewFavorite.objects.filter(user=user, crew=crew).delete()
        else:
            CrewFavorite.objects.create(user=user, crew=crew)
        return Response(status=status.HTTP_200_OK)
    
    # 즐겨찾기 수 기준 상위 6개 크루 조회
    @action(detail=False, methods=["get"])
    def top6(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(is_opened=True).annotate(favorite_count=Count("crewfavorite")).order_by("-favorite_count")[:6]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


"""
크루 관리자 전용

- 크루 관리자만 접근 가능
- 크루 생성/수정/삭제 기능
"""
class ManagerCrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewListSerializer
    permission_classes = [IsAuthenticated, IsCrewAdmin]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CrewDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CrewCreateSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # 현재 사용자가 소유한 크루만 조회
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user).order_by("-id")
        return queryset

    # 크루 생성 시 owner 설정
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # 크루 수정 시 권한 체크
    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsCrewAdmin, IsCrewOwner]
        else:
            permission_classes = [IsAuthenticated, IsCrewAdmin]
        return [permission() for permission in permission_classes]


"""
크루 리뷰 관리

- 크루 리뷰 목록: 모든 사용자가 볼 수 있음
- 리뷰 작성: 크루 회원("member") 또는 탈퇴한 회원("quit")만 가능
- 리뷰 수정/삭제: 해당 작성자만 가능
"""

# 크루 회원 또는 탈퇴한 회원인지 확인하는 메서드
def has_permission_to_create(self, crew):
    return IsCrewMemberOrQuit().has_object_permission(self.request, self, crew)

# 권한 체크 로직을 담고 있는 믹스인 클래스
class CrewReviewPermissionMixin:
    # 리뷰 작성 권한 체크 메서드
    def has_permission_to_create(self, crew):
        return IsCrewMemberOrQuit().has_object_permission(self.request, self, crew)

    # 리뷰 수정/삭제 권한 체크 메서드
    def has_permission_to_update_or_destroy(self, instance):
        return instance.author == self.request.user


# CrewReviewPermissionMixin을 상속받아 권한 체크 로직을 사용하는 ViewSet
class CrewReviewViewSet(CrewReviewPermissionMixin, viewsets.ModelViewSet):
    queryset = CrewReview.objects.select_related("author", "crew")
    serializer_class = CrewReviewListSerializer

    # 리뷰 작성, 수정 시 사용할 serializer 클래스 지정
    def get_serializer_class(self):
        if self.action == "create":
            return CrewReviewCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CrewReviewUpdateSerializer
        return super().get_serializer_class()

    # 특정 크루의 리뷰만 조회
    def get_queryset(self):
        return super().get_queryset().filter(crew_id=self.kwargs.get("crew_id"))

    # 리뷰 작성 기능
    def create(self, request, *args, **kwargs):
        crew = get_object_or_404(Crew, id=self.kwargs.get("crew_id"))
        if not self.has_permission_to_create(crew):
            return Response({"error": "리뷰 작성 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 리뷰 작성 시 저장 로직
    def perform_create(self, serializer):
        crew = get_object_or_404(Crew, id=self.kwargs.get("crew_id"))
        serializer.save(author=self.request.user, crew=crew)

    # 리뷰 수정 기능
    def perform_update(self, serializer):
        if not self.has_permission_to_update_or_destroy(serializer.instance):
            return Response({"error": "리뷰 작성자만 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    # 리뷰 삭제 기능
    def perform_destroy(self, instance):
        if not self.has_permission_to_update_or_destroy(instance):
            return Response({"error": "리뷰 작성자만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


"""
크루 멤버 관리

- 크루 관리자만 접근 가능
- 크루 회원들의 상태(member, quit, keeping 등)를 관리
"""
class CrewMemberViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = JoinedCrew.objects.all()
    serializer_class = JoinedCrewSerializer
    permission_classes = [IsAuthenticated, IsCrewAdmin]

    # 현재 사용자가 소유한 크루의 회원만 조회
    def get_queryset(self):
        crew_id = self.kwargs.get("crew_id")
        return JoinedCrew.objects.filter(crew_id=crew_id, crew__owner=self.request.user)