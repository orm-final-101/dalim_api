from rest_framework import serializers
from .models import Crew, CrewReview
from accounts.models import JoinedCrew
from config.constants import MEET_DAY_CHOICES, TIME_CHOICES


# 크루 목록
class CrewListSerializer(serializers.ModelSerializer):
    is_opened = serializers.CharField(source="get_status_display")
    meet_days = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ["id", "name", "thumbnail_image", "is_favorite", "location_city", "location_district", "meet_days", "meet_time", "is_opened"]

    def get_meet_days(self, obj):
        return obj.meet_days

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.is_favorite(user)
        return False


# 크루 상세
class CrewDetailSerializer(serializers.ModelSerializer):
    is_opened = serializers.CharField(source="get_status_display")
    meet_days = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ["id", "name", "location_city", "location_district", "meet_days", "meet_time", "description", "thumbnail_image", "sns_link", "is_favorite", "is_opened"]

    def get_meet_days(self, obj):
        return obj.meet_days

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.is_favorite(user)
        return False


# 크루 리뷰 CRUD
class CrewReviewListSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source="author.email", read_only=True)
    author_nickname = serializers.CharField(source="author.nickname", read_only=True)

    class Meta:
        model = CrewReview
        fields = ["id", "author_email", "author_nickname", "contents", "created_at", "updated_at"]


class CrewReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewReview
        fields = ["contents"]


class CrewReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewReview
        fields = ["contents"]


# 크루 생성, 수정
class CrewCreateSerializer(serializers.ModelSerializer):
    meet_days = serializers.MultipleChoiceField(choices=MEET_DAY_CHOICES)
    meet_time = serializers.ChoiceField(choices=TIME_CHOICES)

    class Meta:
        model = Crew
        fields = ["name", "location_city", "location_district", "meet_days", "meet_time", "description", "thumbnail_image", "sns_link", "is_opened"]


# 크루 멤버
class JoinedCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedCrew
        fields = ["id", "user", "status"]


# 유저 오픈프로필에서 크루후기 볼 때 사용
class ProfileCrewReviewSerializer(serializers.ModelSerializer):
    crew_id = serializers.IntegerField(source="crew.id")
    title = serializers.CharField(source="crew.name")

    class Meta:
        model = CrewReview
        fields = ["crew_id", "title", "contents"]
