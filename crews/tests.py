from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from .models import Crew, CrewReview, CrewFavorite
from accounts.models import JoinedCrew


User = get_user_model()

# 일반 크루 페이지
class PublicCrewViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="testuser@example.com", password="testpassword")
        self.opened_crew1 = Crew.objects.create(name="Test Crew 1", location_city="seoul", meet_days=["mon", "tue"], is_opened=True, owner=self.user)
        self.opened_crew2 = Crew.objects.create(name="Test Crew 2", location_city="busan", meet_days=["wed", "thu"], is_opened=True, owner=self.user)
        self.closed_crew = Crew.objects.create(name="Test Crew 3", location_city="seoul", meet_days=["fri", "sat"], is_opened=False, owner=self.user)

    # 크루 리스트에서 모집중인 크루만 표시
    def test_crew_list_shows_only_opened_crews(self):
        url = reverse("crews:public_crew-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertContains(response, self.opened_crew1.name)
        self.assertContains(response, self.opened_crew2.name)
        self.assertNotContains(response, self.closed_crew.name)

    # 크루 리스트 검색
    def test_crew_list_search(self):
        url = reverse("crews:public_crew-list") + "?search=Test"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    # 지역 필터링 기능
    def test_filter_by_location_city(self):
        url = reverse("crews:public_crew-list") + "?location_city=seoul"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, self.opened_crew1.name)

    # 요일 필터링 기능
    def test_filter_by_meet_days(self):
        url = reverse("crews:public_crew-list") + "?meet_days=mon&meet_days=tue"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertContains(response, self.opened_crew1.name)

    # 크루 상세정보
    def test_crew_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:public_crew-detail", kwargs={"pk": self.opened_crew1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Crew 1")

    # 크루 가입 신청
    def test_crew_join(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:public_crew-join", kwargs={"pk": self.opened_crew1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(JoinedCrew.objects.filter(user=self.user, crew=self.opened_crew1, status="keeping").exists())

    # 크루 즐겨찾기 추가/해제
    def test_crew_favorite(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:public_crew-favorite", kwargs={"pk": self.opened_crew1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CrewFavorite.objects.filter(user=self.user, crew=self.opened_crew1).exists())

    # 크루 리뷰 작성
    def test_crew_review_list_create(self):
        self.client.force_authenticate(user=self.user)
        JoinedCrew.objects.create(user=self.user, crew=self.opened_crew1, status="member")
        url = reverse("crews:crewreview-list", kwargs={"crew_id": self.opened_crew1.pk})
        data = {"contents": "Test review"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CrewReview.objects.count(), 1)

    # 크루 리뷰 수정/삭제
    def test_crew_review_update_delete(self):
        self.client.force_authenticate(user=self.user)
        review = CrewReview.objects.create(crew=self.opened_crew1, author=self.user, contents="Test review")
        url = reverse("crews:crewreview-detail", kwargs={"crew_id": self.opened_crew1.pk, "pk": review.pk})
        data = {"contents": "Updated review"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CrewReview.objects.get().contents, "Updated review")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CrewReview.objects.count(), 0)

    # 탈퇴("quit")유저의 리뷰 작성/수정/삭제 가능여부
    def test_crew_review_permission_allowed_for_quit_user(self):
        self.client.force_authenticate(user=self.user)
        review = CrewReview.objects.create(crew=self.opened_crew1, author=self.user, contents="Test review")
        url = reverse("crews:crewreview-detail", kwargs={"crew_id": self.opened_crew1.pk, "pk": review.pk})
        data = {"contents": "Updated review"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# 크루 관리자
class ManagerCrewViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.crew_user = User.objects.create_user(email="crewuser@example.com", password="testpassword", user_type="crew")
        self.normal_user = User.objects.create_user(email="normaluser@example.com", password="testpassword", user_type="normal")
        self.crew1 = Crew.objects.create(name="Test Crew 1", location_city="seoul", meet_days=["mon", "tue"], owner=self.crew_user)
        self.crew2 = Crew.objects.create(name="Test Crew 2", location_city="busan", meet_days=["wed", "thu"], owner=self.crew_user)
        self.crew3 = Crew.objects.create(name="Test Crew 3", location_city="seoul", meet_days=["fri", "sat"], owner=self.normal_user)

    # 크루 목록
    def test_crew_list_for_crew_admin(self):
        self.client.force_authenticate(user=self.crew_user)
        url = reverse("crews:manage_crew-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertContains(response, self.crew1.name)
        self.assertContains(response, self.crew2.name)

    # 크루 상세정보
    def test_crew_detail_for_crew_admin(self):
        self.client.force_authenticate(user=self.crew_user)
        url = reverse("crews:manage_crew-detail", kwargs={"pk": self.crew1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Crew 1")

    # 일반회원("normal")의 관리자 페이지 접근 가능여부
    def test_crew_list_permission_denied_for_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse("crews:manage_crew-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_detail_permission_denied_for_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse("crews:manage_crew-detail", kwargs={"pk": self.crew1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 크루 생성 ("owner"는 해당 유저로 자동 할당)
    def test_crew_create(self):
        self.client.force_authenticate(user=self.crew_user)
        url = reverse("crews:manage_crew-list")
        data = {
            "name": "New Test Crew",
            "location_city": "seoul",
            "location_district": "Gangnam",
            "meet_days": ["mon", "wed"],
            "meet_time": "19:00 PM",
            "description": "Test description",
            "thumbnail_image": "",
            "sns_link": "http://example.com",
            "is_opened": True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Crew.objects.count(), 4)

    # 크루 정보 수정
    def test_crew_update(self):
        self.client.force_authenticate(user=self.crew_user)
        url = reverse("crews:manage_crew-detail", kwargs={"pk": self.crew1.pk})
        data = {"name": "Updated Crew Name"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Crew.objects.get(pk=self.crew1.pk).name, "Updated Crew Name")

    # 일반회원("normal")의 크루 정보 수정페이지 접근 가능여부
    def test_crew_update_permission_denied(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse("crews:manage_crew-detail", kwargs={"pk": self.crew1.pk})
        data = {"name": "Updated Crew Name"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# 크루 멤버 관리
class CrewMemberViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.crew_user = User.objects.create_user(email="crewuser@example.com", password="testpassword", user_type="crew")
        self.normal_user = User.objects.create_user(email="normaluser@example.com", password="testpassword", user_type="normal")
        self.crew = Crew.objects.create(name="Test Crew", location_city="seoul", owner=self.crew_user)
        self.member = User.objects.create_user(email="testmember@example.com", password="testpassword")
        self.joined_crew = JoinedCrew.objects.create(user=self.member, crew=self.crew, status="member")

    # 크루 멤버 목록
    def test_crew_member_list(self):
        self.client.force_authenticate(user=self.crew_user)
        url = reverse("crews:joinedcrew-list", kwargs={"crew_id": self.crew.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # 크루 멤버 상태 수정
    def test_crew_member_update(self):
        self.client.force_authenticate(user=self.crew_user)
        url = reverse("crews:joinedcrew-detail", kwargs={"crew_id": self.crew.pk, "pk": self.joined_crew.pk})
        data = {"status": "quit"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(JoinedCrew.objects.get().status, "quit")

    # 일반회원("normal") 접근 가능여부
    def test_crew_member_update_permission_denied(self):
        self.client.force_authenticate(user=self.normal_user)
        url = reverse("crews:joinedcrew-detail", kwargs={"crew_id": self.crew.pk, "pk": self.joined_crew.pk})
        data = {"status": "quit"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)