from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.conf import settings
from crews.models import Crew
from races.models import Race
from config.constants import CREW_CHOICES, GENDER_CHOICES, USER_TYPE_CHOICES, LOCATION_CITY_CHOICES

class LevelStep(models.Model):
    number = models.IntegerField()
    title = models.CharField(max_length=30)
    min_distance = models.IntegerField()
    max_distance = models.IntegerField()

    def __str__(self):
        return f"{self.number} / {self.title}"


class JoinedCrew(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='crews')
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, related_name='members') # 민경 작업 crew 모델과 연결
    status = models.CharField(max_length=20, choices=CREW_CHOICES, default=CREW_CHOICES[0])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.crew}"
    

class JoinedRace(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='races')
    race = models.ForeignKey(Race, on_delete=models.CASCADE) # 유선 작업 race 모델과 연결
    record = models.IntegerField(blank=True, null=True) # 기록
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    race_record = models.CharField(max_length=100, blank=True, null=True) # 대회 기록. 10:00:00 형식으로 들어감

    def __str__(self):
        return f"{self.user.username} - {self.race}"


class Record(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='records')
    description = models.TextField(blank=True, null=True) # 기록 설명
    distance = models.IntegerField(default=0) # 거리 (m)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.distance}m"
                            

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    first_name = None
    last_name = None

    username = models.CharField(max_length=30) # 유저실명
    nickname = models.CharField(max_length=30) # 닉네임
    birth_date = models.DateField(blank=True, null=True) # 생년월일
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default=GENDER_CHOICES[0]) # 성별. default "none"
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default=USER_TYPE_CHOICES[0]) # 유저타입. default "normal"
    location_city = models.CharField(max_length=30, choices=LOCATION_CITY_CHOICES, blank=True, null=True) # 거주지역(시/도)
    location_district = models.CharField(max_length=30, blank=True, null=True) # 거주지역(구/군 등 자유입력)
    phone_number = models.CharField(max_length=20, blank=True, null=True) # 전화번호 (010-1234-5678 형식)
    level = models.ForeignKey(LevelStep, on_delete=models.SET_NULL, blank=True, null=True) # 레벨
    profile_image = models.ImageField(upload_to='accounts/profile/%Y/%m/%d/', blank=True, null=True) # 프로필 이미지


    def __str__(self):
        return f"{self.email} / {self.username}"