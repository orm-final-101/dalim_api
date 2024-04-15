from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser, Record, JoinedCrew, JoinedRace, LevelStep
from crews.models import Crew, CrewFavorite
from races.models import Race, RaceFavorite


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 레벨 2개 생성
        self.level1 = LevelStep.objects.create(
            number=1,
            title="level1",
            min_distance=0,
            max_distance=1000
        )
        self.level1.save()
        self.level2 = LevelStep.objects.create(
            number=2,
            title="level2",
            min_distance=1000,
            max_distance=3000
        )

        # 유저 2명 생성
        self.user = CustomUser.objects.create_user(email="test1@test.com", password="test1234!", level=self.level1)
        self.user.save()

        self.user2 = CustomUser.objects.create_user(email="test2@test.com", password="test1234!", level=self.level2)
        self.user2.save()

        # 기록 3개 생성 (유저1이 2개, 유저2가 1개)
        self.record1 = Record.objects.create(user=self.user, description = "record 1", distance=800)
        self.record1.save()

        self.record2 = Record.objects.create(user=self.user, description = "record 2", distance=80)
        self.record2.save()

        self.record3 = Record.objects.create(user=self.user2, description = "record 3", distance=600)
        self.record3.save()

        # 크루 1개 생성
        self.crew1 = Crew.objects.create(
            owner=self.user,
            name="crew1",
            location_city="city1",
            location_district="district1",
            meet_days=["mon", "tue"],
            meet_time="10:00:00",
            description="crew1 description",
            thumbnail_image="test.jpg",
            sns_link="http://test.com",
            is_opened=True
        )
        self.crew1.save()
        self.crew2 = Crew.objects.create(
            owner=self.user,
            name="crew2",
            location_city="city2",
            location_district="district2",
            meet_days=["wed", "thu"],
            meet_time="12:00:00",
            description="crew2 description",
            thumbnail_image="test.jpg",
            sns_link="http://test.com",
            is_opened=True
        )

        # 크루 가입 정보 2개 생성 (유저1이 크루1, 크루2에 가입)
        self.joined_crew1 = JoinedCrew.objects.create(
            user=self.user,
            crew=self.crew1,
            status="member"
        )
        self.joined_crew1.save()
        
        self.joined_crew2 = JoinedCrew.objects.create(
            user=self.user,
            crew=self.crew2,
            status="keeping"
        )

        # 대회 2개 생성
        self.race1 = Race.objects.create(
            title = "대회1",
            organizer = "주최자1",
            description = "대회1 설명",
            start_date = "2024-04-15",
            end_date = "2024-04-16",
            reg_start_date = "2024-04-08",
            reg_end_date = "2024-04-10",
            courses = ["full", "half"],
            thumbnail_image = "test.jpg",
            author = self.user,
            location = "대회1 장소",
            fees = 5000,
            register_url = "http://test.com"
        )
        self.race1.save()

        self.race2 = Race.objects.create(
            title = "대회2",
            organizer = "주최자2",
            description = "대회2 설명",
            start_date = "2024-04-15",
            end_date = "2024-04-16",
            reg_start_date = "2024-04-08",
            reg_end_date = "2024-04-09",
            courses = ["full"],
            thumbnail_image = "test.jpg",
            author = self.user,
            location = "대회2 장소",
            fees = 0,
            register_url = "http://test.com"
        )

        # 대회 가입 정보 2개 생성 (유저1이 대회1, 유저2가 대회2에 가입)
        self.joined_race1 = JoinedRace.objects.create(
            user=self.user,
            race=self.race1
        )
        self.joined_race1.save()

        self.joined_race2 = JoinedRace.objects.create(
            user=self.user2,
            race=self.race2
        )

        # 크루, 대회 좋아요 정보 2개 생성 (유저1이 크루1, 대회1에 좋아요)
        self.crew_favorite1 = CrewFavorite.objects.create(
            user=self.user,
            crew=self.crew1
        )
        self.crew_favorite1.save()
        self.race_favorite1 = RaceFavorite.objects.create(
            user=self.user,
            race=self.race1
        )


class MypageInfoTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
    
    def test_get_mypage_info(self):
        print("[마이페이지 info GET 테스트]")
        print(">> 비회원 상태에서 마이페이지 정보를 요청하면 401을 반환한다.")
        response = self.client.get("/accounts/mypage/info/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print(response.data)

        print(">> 회원 상태에서 마이페이지 정보를 요청하면 200을 반환한다.")
        self.client.force_authenticate(user=self.user)
        self.user.save()
        response = self.client.get("/accounts/mypage/info/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print("----------------------------------------------------- 완료")


    def test_patch_mypage_info(self):
        print("[마이페이지 info PATCH 테스트]")
        print(">> 비회원 상태에서 마이페이지 정보를 수정하려고 하면 401을 반환한다.")
        response = self.client.patch(f"/accounts/mypage/info/${self.user.pk}/", data={"nickname": "patch test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 마이페이지 정보를 수정하면 200을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f"/accounts/mypage/info/${self.user.pk}/", data={"nickname": "patch test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print("----------------------------------------------------- 완료")


class MypageRecordTestCase(BaseTestCase): 
    def setUp(self):
        super().setUp()

    def test_get_record_list(self):
        print("[기록 GET 테스트]")
        print(">> 비회원 상태에서 기록 리스트를 요청하면 401을 반환한다.")
        response = self.client.get("/accounts/mypage/record/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print(response.data)

        print(">> 회원 상태에서 기록 리스트를 요청하면 200을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/accounts/mypage/record/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print("----------------------------------------------------- 완료")

    def test_post_record(self):
        print("[기록 POST 테스트]")
        print(">> 비회원 상태에서 기록을 추가하려고 하면 401을 반환한다.")
        response = self.client.post("/accounts/mypage/record/", data={"description": "record 4", "distance": 8})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 기록을 추가하면 201을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/accounts/mypage/record/", data={"description": "record 4", "distance": 8})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(response.data)
        print("----------------------------------------------------- 완료")

    def test_patch_record(self):
        print("[기록 PATCH 테스트]")
        print(">> 비회원 상태에서 기록을 수정하려고 하면 401을 반환한다.")
        response = self.client.patch(f"/accounts/mypage/record/{self.record1.id}/", data={"description": "patch test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 다른 유저의 기록을 수정하려고 하면 404을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f"/accounts/mypage/record/{self.record3.id}/", data={"description": "patch test"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print(response.data)

        print(">> 회원 상태에서 자신의 기록을 수정하면 200을 반환한다.")
        response = self.client.patch(f"/accounts/mypage/record/{self.record1.id}/", data={"description": "patch test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print("----------------------------------------------------- 완료")

    def test_delete_record(self):
        print("[기록 DELETE 테스트]")
        print(">> 비회원 상태에서 기록을 삭제하려고 하면 401을 반환한다.")
        response = self.client.delete(f"/accounts/mypage/record/{self.record1.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 다른 유저의 기록을 삭제하려고 하면 404을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/accounts/mypage/record/{self.record3.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print(response.data)

        print(">> 회원 상태에서 자신의 기록을 삭제하면 204을 반환한다.")
        response = self.client.delete(f"/accounts/mypage/record/{self.record1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        print(response.data)
        print("----------------------------------------------------- 완료")


class MypageCrewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_get_crew_list(self):
        print("[크루 GET 테스트]")
        print(">> 비회원 상태에서 크루 리스트를 요청하면 401을 반환한다.")
        response = self.client.get("/accounts/mypage/crew/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 크루 리스트를 요청하면 200을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/accounts/mypage/crew/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print("----------------------------------------------------- 완료")


class MypageRaceTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_get_race_list(self):
        print("[대회기록 GET 테스트]")
        print(">> 비회원 상태에서 대회 리스트를 요청하면 401을 반환한다.")
        response = self.client.get("/accounts/mypage/race/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 대회기록 리스트를 요청하면 200을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/accounts/mypage/race/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print("----------------------------------------------------- 완료")

    def test_post_race(self):
        print("[내 대회 추가 POST 테스트]")
        print(">> 비회원 상태에서 대회를 추가하려고 하면 401을 반환한다.")
        response = self.client.post("/accounts/mypage/race/", data={"race_id":self.race2.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 대회를 추가하면 201을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/accounts/mypage/race/", data={"race_id":self.race2.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(response.data)
        print("----------------------------------------------------- 완료")

    def test_patch_race(self):
        print("[내 대회 기록 수정 PATCH 테스트]")
        print(">> 비회원 상태에서 대회 기록을 수정하려고 하면 401을 반환한다.")
        print("self.joined_race1")
        print(self.joined_race1)
        response = self.client.patch(
            f"/accounts/mypage/race/{self.joined_race1.id}/",
            data={"race_record": "10:00:00"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 다른 유저의 대회 기록을 수정하려고 하면 404을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/accounts/mypage/race/{self.joined_race2.id}/",
            data={"race_record": "10:00:00"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        print(">> 회원 상태에서 자신의 대회 기록을 수정하면 200을 반환한다.")
        response = self.client.patch(
            f"/accounts/mypage/race/{self.joined_race1.id}/",
            data={"race_record": "10:00:00"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print("----------------------------------------------------- 완료")

    def test_delete_race(self):
        print("[내 대회기록 삭제 DELETE 테스트]")
        print(">> 비회원 상태에서 대회기록을 삭제하려고 하면 401을 반환한다.")
        response = self.client.delete(f"/accounts/mypage/race/{self.joined_race1.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 다른 유저의 대회기록을 삭제하려고 하면 404을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/accounts/mypage/race/{self.joined_race2.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        print(">> 회원 상태에서 자신의 대회기록을 삭제하면 204을 반환한다.")
        response = self.client.delete(f"/accounts/mypage/race/{self.joined_race1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        print("----------------------------------------------------- 완료")


class FavoriteTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_get_favorite_list(self):
        print("[좋아요 GET 테스트]")
        print(">> 비회원 상태에서 좋아요 리스트를 요청하면 401을 반환한다.")
        response = self.client.get("/accounts/mypage/favorites/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print(">> 회원 상태에서 좋아요 리스트를 요청하면 200을 반환한다.")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/accounts/mypage/favorites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print("----------------------------------------------------- 완료")
        
class OpenProfileTestCase(BaseTestCase):
    def setUp(self):
        return super().setUp()
    
    def test_nomember(self):
        print("[공개 프로필 GET 테스트]")
        print(">> 비회원 상태에서도 GET 가능. 지정된 형식과 일치하는지 확인")
        response = self.client.get(f"/accounts/profile/{self.user.id}/")
        data = response.data
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", data)
        self.assertIn("id", data["user"])
        self.assertIn("username", data["user"])
        self.assertIn("nickname", data["user"])
        self.assertIn("distance", data["user"])
        self.assertIn("level", data["user"])
        self.assertIn("title", data["user"]["level"])
        self.assertIn("number", data["user"]["level"])
        self.assertIn("next_distance", data["user"]["level"])
        self.assertIn("profile_image", data["user"])
        self.assertIn("crew", data["user"])
        self.assertIn("posts", data)
        self.assertIn("comments", data)
        self.assertIn("reviews", data)
        self.assertNotIn("likes", data) # 본인만 좋아요 리스트 확인 가능
        print("----------------------------------------------------- 완료")

    def test_member(self):
        print("[공개 프로필 GET 테스트]")
        print(">> 회원 상태에서도 GET 가능. 본인일 때에만 좋아요 리스트 확인")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/accounts/profile/{self.user2.id}/")
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("likes", data)

        response = self.client.get(f"/accounts/profile/{self.user.id}/")
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("likes", data)
        print("----------------------------------------------------- 완료")