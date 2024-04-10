from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers
from django.db.models import Sum
from .models import CustomUser, LevelStep, Record, JoinedCrew, JoinedRace


class CustomUserSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = ("pk", "email", "username", "nickname", "user_type", "is_staff")
        

class LevelStepSerializer(serializers.ModelSerializer):
    next_distance = serializers.SerializerMethodField()

    class Meta:
        model = LevelStep
        fields = ["title", "number", "next_distance"]

    def get_next_distance(self, obj):
        return obj.max_distance


class ProfileSerializer(serializers.ModelSerializer):
    level = LevelStepSerializer(read_only=True)
    distance = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ["id", "username", "nickname", "phone_number", "location_city", "location_district", "distance", "level", "profile_image"]

    def get_distance(self, obj):
        # 모든 Record 객체의 distance를 합산합니다.
        # 이 코드는 distance 필드가 Record 모델에 있는 정수 필드라고 가정합니다.
        return Record.objects.filter(user=obj).aggregate(total_distance=Sum("distance"))["total_distance"] or 0
    

class RecordSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ["id", "user", "created_at", "description", "distance"]
        read_only_fields = ["user"]


class JoinedCrewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="crew.id")
    name = serializers.CharField(source="crew.name")
    location_city = serializers.CharField(source="crew.location_city")
    location_district = serializers.CharField(source="crew.location_district")
    meet_days = serializers.SerializerMethodField()
    meet_time = serializers.CharField(source="crew.meet_time")
    thumbnail_image = serializers.ImageField(source="crew.thumbnail_image")

    def get_meet_days(self, obj):
        return obj.crew.meet_days
    class Meta:
        model = JoinedCrew
        fields = ["id", "status", "name", "location_city", "location_district", "meet_days", "meet_time", "thumbnail_image"]
        read_only_fields = ["user"]


class JoinedRaceGetSerializer(serializers.ModelSerializer):
    joined_race_id = serializers.IntegerField(source="id")
    race_id = serializers.IntegerField(source="race.id")
    reg_status = serializers.CharField(source="race.reg_status")
    d_day = serializers.IntegerField(source="race.d_day")
    location = serializers.CharField(source="race.location")
    title = serializers.CharField(source="race.title")
    start_date = serializers.DateField(source="race.start_date")
    end_date = serializers.DateField(source="race.end_date")
    reg_start_date = serializers.DateField(source="race.reg_start_date")
    reg_end_date = serializers.DateField(source="race.reg_end_date")
    courses = serializers.SerializerMethodField()
    record = serializers.CharField(source="race_record")
    thumbnail_image = serializers.ImageField(source="race.thumbnail_image")

    def get_courses(self, obj):
        return obj.race.courses

    class Meta:
        model = JoinedRace
        fields = ["joined_race_id", "race_id", "reg_status", "d_day", "location", "title", "start_date", "end_date", "reg_start_date", "reg_end_date", "courses", "record", "thumbnail_image"]

class JoinedRacePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedRace
        fields = ["user", "race", "race_record"]


class OpenProfileSerializer(ProfileSerializer):
    crew = serializers.SerializerMethodField()

    def get_crew(self, obj):
        return [joined_crew.crew.name for joined_crew in obj.crews.all()]

    class Meta(ProfileSerializer.Meta):
        fields = ["id", "username", "nickname", "location_city", "location_district", "distance", "level", "profile_image", "crew"]