from rest_framework import serializers
from .models import Crew, CrewReview
from accounts.models import JoinedCrew
from config.constants import MEET_DAY_CHOICES, TIME_CHOICES


# 즐겨찾기 여부 체크
def check_is_favorite(user, crew):
    if user.is_authenticated:
        return crew.is_favorite(user)
    return False

class CrewListSerializer(serializers.ModelSerializer):
    is_opened = serializers.CharField(source="get_status_display")
    meet_days = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    favorite_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "name", "thumbnail_image", "member_count", "is_favorite", "location_city", "location_district", "meet_days", "meet_time", "is_opened", "favorite_count"]

    def get_meet_days(self, obj):
        return obj.meet_days

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        return check_is_favorite(user, obj)
    
    def get_member_count(self, obj):
        return JoinedCrew.objects.filter(crew=obj, status="member").count()


class CrewDetailSerializer(serializers.ModelSerializer):
    is_opened = serializers.CharField(source="get_status_display")
    meet_days = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ["id", "name", "location_city", "location_district", "meet_days", "meet_time", "description", "thumbnail_image", "sns_link", "is_favorite", "is_opened", "member_count"]

    def get_meet_days(self, obj):
        return obj.meet_days

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        return check_is_favorite(user, obj)
    
    def get_member_count(self, obj):
        return JoinedCrew.objects.filter(crew=obj, status="member").count()


class CrewReviewListSerializer(serializers.ModelSerializer):
    author_id = serializers.CharField(source="author.id", read_only=True)
    author_nickname = serializers.CharField(source="author.nickname", read_only=True)

    class Meta:
        model = CrewReview
        fields = ["id", "author_id", "author_nickname", "contents", "created_at", "updated_at"]


class CrewReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewReview
        fields = ["contents"]


class CrewReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewReview
        fields = ["contents"]


class CrewCreateSerializer(serializers.ModelSerializer):
    meet_days = serializers.MultipleChoiceField(choices=MEET_DAY_CHOICES)
    meet_time = serializers.ChoiceField(choices=TIME_CHOICES)

    class Meta:
        model = Crew
        fields = ["name", "location_city", "location_district", "meet_days", "meet_time", "description", "thumbnail_image", "sns_link", "is_opened"]


class JoinedCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedCrew
        fields = ["id", "user", "status"]


# 유저 오픈프로필에서 크루후기 볼 때 사용 > accounts
class ProfileCrewReviewSerializer(serializers.ModelSerializer):
    crew_id = serializers.IntegerField(source="crew.id")
    title = serializers.CharField(source="crew.name")

    class Meta:
        model = CrewReview
        fields = ["crew_id", "title", "contents"]