from rest_framework import serializers
from .models import RaceReview


# 유저 오픈프로필에서 크루후기 볼 때 사용
class ProfileRaceReviewSerializer(serializers.ModelSerializer):
    race_id = serializers.IntegerField(source="race.id")
    title = serializers.CharField(source="race.title")

    class Meta:
        model = RaceReview
        fields = ["race_id", "title", "contents"]
