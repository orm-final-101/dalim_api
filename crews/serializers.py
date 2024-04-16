from rest_framework import serializers
from .models import Crew, CrewReview
from accounts.models import JoinedCrew
from config.constants import MEET_DAY_CHOICES, TIME_CHOICES


# 즐겨찾기 여부 체크
def check_is_favorite(user, crew):
    if user.is_authenticated:
        return crew.is_favorite(user)
    return False

"""
크루 시리얼라이저에서 공통으로 사용되는 메서드 정의

- get_meet_days: 모임 요일을 반환. `["mon", "tue"]`의 형태로 제공.
- get_is_favorite: 크루의 즐겨찾기 여부 반환
- get_member_count: 크루의 멤버 수를 반환
"""
class CrewSerializerMixin:
    def get_meet_days(self, obj):
        return obj.meet_days

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        return check_is_favorite(user, obj)
    
    def get_member_count(self, obj):
        return JoinedCrew.objects.filter(crew=obj, status="member").count()


"""
크루 리스트 시리얼라이저

- is_opened: 모집여부
- meet_days: 만나는 요일
- is_favorite: 해당 크루에 대한 즐겨찾기 여부
- member_count: 해당 크루의 총 멤버 수
- favorite_count: 해당 크루의 총 즐겨찾기 수 (top6에 사용됨)
"""
class CrewListSerializer(CrewSerializerMixin, serializers.ModelSerializer):
    is_opened = serializers.CharField(source="get_status_display")
    meet_days = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    favorite_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "name", "thumbnail_image", "member_count", "is_favorite", "location_city", "location_district", "meet_days", "meet_time", "is_opened", "favorite_count"]


"""
크루 상세 시리얼라이저

- is_opened: 모집여부
- meet_days: 만나는 요일
- is_favorite: 해당 크루에 대한 즐겨찾기 여부
- member_count: 해당 크루의 총 멤버 수
"""
class CrewDetailSerializer(CrewSerializerMixin, serializers.ModelSerializer):
    is_opened = serializers.CharField(source="get_status_display")
    meet_days = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ["id", "name", "location_city", "location_district", "meet_days", "meet_time", "description", "thumbnail_image", "sns_link", "is_favorite", "is_opened", "member_count"]


"""
크루 리뷰 리스트 시리얼라이저

- author_id: 해당 리뷰를 쓴 유저의 id(pk)값
- author_nickname = 해당 리뷰를 쓴 유저의 닉네임
"""
class CrewReviewListSerializer(serializers.ModelSerializer):
    author_id = serializers.CharField(source="author.id", read_only=True)
    author_nickname = serializers.CharField(source="author.nickname", read_only=True)

    class Meta:
        model = CrewReview
        fields = ["id", "author_id", "author_nickname", "contents", "created_at", "updated_at"]


"""
크루 리뷰 작성 시리얼라이저

- contents: 댓글 내용
- "id", "author_id", "author_nickname", "created_at", "updated_at" 는 자동 할당
"""
class CrewReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewReview
        fields = ["contents"]


"""
크루 리뷰 수정 시리얼라이저

- contents: 댓글 내용
- "id", "author_id", "author_nickname", "created_at", "updated_at" 는 자동 할당
"""
class CrewReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewReview
        fields = ["contents"]


"""
크루 생성 시 사용되는 시리얼라이저

- meet_days: 크루 모임 요일 (다중 선택 가능)
- meet_time: 크루 모임 시간대
"""
class CrewCreateSerializer(serializers.ModelSerializer):
    meet_days = serializers.MultipleChoiceField(choices=MEET_DAY_CHOICES)
    meet_time = serializers.ChoiceField(choices=TIME_CHOICES)

    class Meta:
        model = Crew
        fields = ["name", "location_city", "location_district", "meet_days", "meet_time", "description", "thumbnail_image", "sns_link", "is_opened"]


"""
크루 정보 수정 시 사용되는 시리얼라이저
"""
class CrewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["name", "location_city", "location_district", "meet_days", "meet_time", "description", "thumbnail_image", "sns_link", "is_opened"]


"""
가입된 크루 조회 시 사용되는 시리얼라이저

- username: 사용자 아이디 (읽기 전용)
- email: 사용자 이메일 (읽기 전용)
- updated_at: 사용자 최근 로그인 시간 (읽기 전용)
"""
class JoinedCrewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    updated_at = serializers.CharField(source="user.last_login", read_only=True)

    class Meta:
        model = JoinedCrew
        fields = ["id", "username", "email", "updated_at", "status"]


"""
유저 오픈프로필에서 크루 리뷰 조회 시 사용되는 시리얼라이저 (accounts 앱에서 사용)

- crew_id: 크루 ID
- title: 크루 이름
"""
class ProfileCrewReviewSerializer(serializers.ModelSerializer):
    crew_id = serializers.IntegerField(source="crew.id")
    title = serializers.CharField(source="crew.name")

    class Meta:
        model = CrewReview
        fields = ["crew_id", "title", "contents"]