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


# 일반 크루 페이지
class PublicCrewViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CrewListSerializer

    def get_queryset(self):
        return Crew.objects.filter(is_opened=True)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CrewDetailSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def filter_queryset(self, queryset):
        search_keyword = self.request.GET.get("search", "")
        selected_location_city = self.request.GET.get("location_city", "")
        selected_meet_days = self.request.GET.get("meet_days", "")

        if search_keyword:
            queryset = queryset.filter(
                Q(name__icontains=search_keyword) |
                Q(description__icontains=search_keyword)
            )

        if selected_location_city:
            selected_location_city = [city[0] for city in LOCATION_CITY_CHOICES if city[0] == selected_location_city]
            if selected_location_city:
                queryset = queryset.filter(location_city=selected_location_city[0])

        if selected_meet_days:
            selected_meet_days = selected_meet_days.split(",")
            valid_meet_days = [day[0] for day in MEET_DAY_CHOICES]
            selected_meet_days = [day for day in selected_meet_days if day in valid_meet_days]
            query = Q()
            for day in selected_meet_days:
                query |= Q(meet_days__contains=day)
            queryset = queryset.filter(query)

        return queryset

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

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        crew = self.get_object()
        user = request.user

        if CrewFavorite.objects.filter(user=user, crew=crew).exists():
            CrewFavorite.objects.filter(user=user, crew=crew).delete()
        else:
            CrewFavorite.objects.create(user=user, crew=crew)

        return Response(status=status.HTTP_200_OK)
    
    # 즐겨찾기순으로 top6
    @action(detail=False, methods=["get"])
    def popular(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(is_opened=True).annotate(favorite_count=Count("crewfavorite")).order_by("-favorite_count")[:6]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 크루 관리자 전용
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

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsCrewAdmin, IsCrewOwner]
        else:
            permission_classes = [IsAuthenticated, IsCrewAdmin]
        return [permission() for permission in permission_classes]


# 크루 리뷰
class CrewReviewViewSet(viewsets.ModelViewSet):
    queryset = CrewReview.objects.all()
    serializer_class = CrewReviewListSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CrewReviewCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CrewReviewUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        crew_id = self.kwargs.get("crew_id")
        return CrewReview.objects.filter(crew_id=crew_id)

    def create(self, request, *args, **kwargs):
        crew_id = self.kwargs.get("crew_id")
        crew = get_object_or_404(Crew, id=crew_id)

        if not IsCrewMemberOrQuit().has_object_permission(request, self, crew):
            return Response({"error": "리뷰 작성 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        crew_id = self.kwargs.get("crew_id")
        crew = get_object_or_404(Crew, id=crew_id)
        serializer.save(author=self.request.user, crew=crew)

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def check_object_permissions(self, request, obj):
        if self.action in ["update", "partial_update", "destroy"]:
            if request.user != obj.author:
                self.permission_denied(request, message="리뷰 작성자만 수정/삭제할 수 있습니다.")
        return super().check_object_permissions(request, obj)


# 크루 멤버관리
class CrewMemberViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = JoinedCrew.objects.all()
    serializer_class = JoinedCrewSerializer
    permission_classes = [IsAuthenticated, IsCrewAdmin]

    def get_queryset(self):
        crew_id = self.kwargs.get("crew_id")
        return JoinedCrew.objects.filter(crew_id=crew_id, crew__owner=self.request.user)