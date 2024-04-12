from rest_framework import serializers
from .models import Race, RaceReview


def check_is_favorite(user, race):
    if user.is_authenticated:
        return race.is_favorite(user)
    return False

class RaceListSerializer(serializers.ModelSerializer):
    reg_status = serializers.CharField()
    is_favorite = serializers.SerializerMethodField()
    d_day = serializers.IntegerField()

    class Meta:
        model = Race
        fields = ["id", "title", "reg_status", "d_day", "location", "start_date", "end_date", "reg_start_date", "reg_end_date", "courses", "thumbnail_image", "is_favorite"]

    def get_reg_status(self, obj):
        return obj.reg_status()

    def get_d_day(self, obj):
        return obj.d_day()

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        return check_is_favorite(user, obj)
    

class RaceDetailSerializer(serializers.ModelSerializer):
    reg_status = serializers.SerializerMethodField()
    d_day = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    
    class Meta:
        model = Race
        fields = ["id", "title", "organizer", "description", "start_date", "end_date", "reg_start_date", "reg_end_date", "courses", "thumbnail_image", "location", "fees", "reg_status", "d_day", "is_favorite", "register_url"]

    def get_reg_status(self, obj):
        return obj.reg_status()

    def get_d_day(self, obj):
        return obj.d_day()

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.is_favorite(user)
        return False

class RaceReviewSerializer(serializers.ModelSerializer): 
    class Meta:
        model = RaceReview
        fields = ["id", "author", "contents", "created_at", "updated_at"]
        
        
# 유저 오픈프로필에서 크루후기 볼 때 사용
class ProfileRaceReviewSerializer(serializers.ModelSerializer):
    race_id = serializers.IntegerField(source="race.id")
    title = serializers.CharField(source="race.title")

    class Meta:
        model = RaceReview
        fields = ["race_id", "title", "contents"]
