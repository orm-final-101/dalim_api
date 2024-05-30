from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from races.models import Race, RaceReview, RaceFavorite
from accounts.models import CustomUser, LevelStep
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


# 대회 생성/삭제/수정은 어드민에서만 가능. 이를 위한 기능 개발 없음
class RaceTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 레벨 2개 생성
        self.level1 = LevelStep.objects.create(
            number=1, title="Level 1", min_distance=5, max_distance=200
        )
        self.level2 = LevelStep.objects.create(
            number=2, title="Level 2", min_distance=10, max_distance=2000
        )

        # 유저 2개 생성
        self.user1 = CustomUser.objects.create_user(
            username="test1",
            email="test1@test.com",
            password="test1234!",
            level=self.level1,
        )
        self.user2 = CustomUser.objects.create_user(
            username="test2",
            email="test2@test.com",
            password="test1234!",
            level=self.level2,
        )

        # 대회2개 생성
        self.race1 = Race.objects.create(
            title="대회1",
            organizer="주최자1",
            description="대회1 설명",
            start_date=date(2024, 4, 15),
            end_date=date(2024, 4, 16),
            reg_start_date=date(2024, 4, 8),
            reg_end_date=date(2024, 4, 12),
            thumbnail_image="test.jpg",
            author=self.user1,
            location="대회1 장소",
            fees=5000,
            register_url="http://test.com",
            courses=["full", "half"],
        )

        self.race2 = Race.objects.create(
            title="대회2",
            organizer="주최자2",
            description="대회2 설명",
            start_date=date(2024, 4, 15),
            end_date=date(2024, 4, 16),
            reg_start_date=date(2024, 4, 8),
            reg_end_date=date(2024, 4, 9),
            thumbnail_image="test.jpg",
            author=self.user2,
            location="대회2 장소",
            fees=0,
            register_url="http://test.com",
            courses=["full", "half", "10km"],
        )

        # 대회1의 리뷰2개 생성
        self.racereview1_1 = RaceReview.objects.create(
            race=self.race1,
            author=self.user1,
            contents="날씨가 덥지 않기를 바래요",
            created_at=date(2024, 4, 11),
            updated_at=date(2024, 4, 11),
        )
        self.racereview1_2 = RaceReview.objects.create(
            race=self.race1,
            author=self.user2,
            contents="날씨가 덥지 않기를 바래요 222222",
            created_at=date(2024, 4, 12),
            updated_at=date(2024, 4, 12),
        )

        # 대회2의 리뷰2개 생성
        self.racereview2_1 = RaceReview.objects.create(
            race=self.race2,
            author=self.user1,
            contents="I hope the weather is not hot.",
            created_at=date(2024, 4, 9),
            updated_at=date(2024, 4, 9),
        )
        self.racereview2_2 = RaceReview.objects.create(
            race=self.race2,
            author=self.user2,
            contents="So do I",
            created_at=date(2024, 4, 12),
            updated_at=date(2024, 4, 12),
        )

    # 대회 목록 조회 테스트
    def test_race_list_view(self):
        print("[대회 목록 조회 테스트]")
        print(">> 로그인 상태 확인 없이 요청하면 대회 목록을 반환한다. ")
        response = self.client.get("/races/")
        self.assertEqual(response.status_code, 200)
        print(response.data)
        print(
            "------------------------------------------------------------------------완료 "
        )

    # 대회 상세 조회 테스트
    def test_race_detail_view(self):
        print("[대회 상세 조회 테스트]")
        print(">> 로그인 상태 확인 없이 요청하면 대회 상세를 반환한다. ")
        response = self.client.get("/races/1/")
        self.assertEqual(response.status_code, 200)
        print(response.data)
        print(
            "------------------------------------------------------------------------완료 "
        )

    # 접수중 대회 6개 목록 조회 테스트
    def test_race_top6_list_view(self):
        print("[접수중 대회 6개 목록 조회 테스트]")
        print(
            ">> 로그인 상태 확인 없이 요청하면 대회 목록을 반환한다. 메인페이지에 표시 "
        )
        today = date.today()
        open_races = Race.objects.filter(
            reg_start_date__lte=today, reg_end_date__gte=today
        )
        sorted_races = sorted(open_races, key=lambda x: x.d_day(), reverse=False)[:6]
        response = self.client.get("/races/top6/")
        self.assertEqual(response.status_code, 200)
        print(response.data)
        print(
            "------------------------------------------------------------------------완료 "
        )

    # 대회 리뷰 목록 조회 테스트
    def test_race_reviews_list_view(self):
        print("[대회 리뷰 목록 조회 테스트]")
        print(">> 로그인 상태 확인 없이, 요청하면 대회 리뷰 목록을 반환한다.")
        response = self.client.get("/races/1/reviews/")
        self.assertEqual(response.status_code, 200)
        print(response.data)
        print(
            "------------------------------------------------------------------------완료 "
        )
