from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from .models import Crew, CrewReview, CrewFavorite
from accounts.models import JoinedCrew


User = get_user_model()

class CrewListViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com")
        self.crew = Crew.objects.create(name="Test Crew", location_city="seoul", location_district="Gangnam", owner=self.user)

    def test_crew_list_view(self):
        url = reverse("crews:crew_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_crew_list_search(self):
        url = reverse("crews:crew_list") + "?search=Test"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CrewDetailViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com")
        self.crew = Crew.objects.create(name="Test Crew", location_city="seoul", location_district="Gangnam", owner=self.user)

    def test_crew_detail_view(self):
        url = reverse("crews:crew_detail", args=[self.crew.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Crew")


class CrewJoinViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com")
        self.crew = Crew.objects.create(name="Test Crew", location_city="seoul", location_district="Gangnam", owner=self.user)

    def test_crew_join_apply(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:crew_join", args=[self.crew.id])
        data = {"action": "apply"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(JoinedCrew.objects.filter(user=self.user, crew=self.crew).exists())


class CrewFavoriteViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com")
        self.crew = Crew.objects.create(name="Test Crew", location_city="seoul", location_district="Gangnam", owner=self.user)

    def test_crew_favorite(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:crew_favorite", args=[self.crew.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CrewFavorite.objects.filter(user=self.user, crew=self.crew).exists())


class CrewReviewViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com")
        self.crew = Crew.objects.create(name="Test Crew", location_city="seoul", location_district="Gangnam", owner=self.user)
        self.joined_crew = JoinedCrew.objects.create(user=self.user, crew=self.crew, status="member")

    def test_crew_review_list_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:crew_review_list_create", args=[self.crew.id])
        data = {"contents": "Test review"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CrewReview.objects.count(), 1)

        another_user = User.objects.create_user(username="anotheruser", password="testpassword", email="another@example.com")
        self.client.force_authenticate(user=another_user)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_review_update_delete(self):
        self.client.force_authenticate(user=self.user)
        review = CrewReview.objects.create(crew=self.crew, author=self.user, contents="Test review")
        url = reverse("crews:crew_review_update_delete", args=[self.crew.id, review.id])
        data = {"contents": "Updated review"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CrewReview.objects.get().contents, "Updated review")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CrewReview.objects.count(), 0)


class CrewCreateUpdateTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com", user_type="crew")
        self.crew_data = {
            "name": "Test Crew",
            "location_city": "seoul",
            "location_district": "Gangnam",
            "meet_days": ["mon", "wed"],
            "meet_time": "19:00 PM",
            "description": "Test description",
            "thumbnail_image": None,
            "sns_link": "http://example.com",
            "is_opened": True
        }

    def test_crew_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:crew_create")
        response = self.client.post(url, data=self.crew_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Crew.objects.count(), 1)

    def test_crew_update(self):
        self.client.force_authenticate(user=self.user)
        crew = Crew.objects.create(name="Test Crew", location_city="seoul", location_district="Jamsil", owner=self.user)
        url = reverse("crews:crew_update", args=[crew.id])
        data = {"name": "Updated Crew"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Crew.objects.get().name, "Updated Crew")


class CrewMemberViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="test@example.com", user_type="crew")
        self.crew = Crew.objects.create(name="Test Crew", location_city="seoul", location_district="Gangnam", owner=self.user)
        self.member = User.objects.create_user(username="testmember", password="testpassword", email="test2@example.com")
        self.joined_crew = JoinedCrew.objects.create(user=self.member, crew=self.crew, status="member")

    def test_crew_member_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:crew_member_list", args=[self.crew.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_crew_member_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("crews:crew_member_update", args=[self.crew.id, self.joined_crew.id])
        data = {"status": "quit"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(JoinedCrew.objects.get().status, "quit")