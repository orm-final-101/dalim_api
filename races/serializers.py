from rest_framework import serializers
from .models import Race, RaceFavorite, RaceReview
from accounts.models import JoinedRace
from config.constants import COURSE_CHOICES

class RaceListSerializer(serializers.ModelSerializer):
    reg_status = serializers.CharField(source="reg_status")
    courses = serializers.MultipleChoiceField(source="courses")
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Race
        fields = ["id", "title", "start_date", "end_date", "reg_start_date", "reg_end_date", "courses", "thumbnail_image", "location", "reg_status", "d_day", "is_favorite"]

    def get_reg_status(self, obj):
        return obj.reg_status()

    def get_d_day(self, obj):
        return obj.d_day()

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.is_favorite(user)
        return False

class RaceDetailSerializer(serializers.ModelSerializer):
    reg_status = serializers.CharField(source="reg_status")
    courses = serializers.MultipleChoiceField(source="courses")
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Race
        fields = ["id", "title", "description", "start_date", "end_date", "reg_start_date", "reg_end_date", "courses", "thumbnail_image", "location", "fees", "reg_status", "d_day", "is_favorite", "register_url"]

    def get_reg_status(self, obj):
        return obj.reg_status()

    def get_d_day(self, obj):
        return obj.d_day()

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.is_favorite(user)
        return False

class RaceReviewListSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source="author", read_only=True)

    class Meta:
        model = RaceReview
        fields = ["id", "author", "contents", "created_at", "updated_at"]

class RaceReviewDetailSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source="author", read_only=True)

    class Meta:
        model = RaceReview
        fields = ["id", "author", "contents", "created_at", "updated_at"] 

class JoinedRaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedRace
        fields = ["id", "user", "status"]       
        
        
# 유저 오픈프로필에서 크루후기 볼 때 사용
class ProfileRaceReviewSerializer(serializers.ModelSerializer):
    race_id = serializers.IntegerField(source="race.id")
    title = serializers.CharField(source="race.title")

    class Meta:
        model = RaceReview
        fields = ["race_id", "title", "contents"]