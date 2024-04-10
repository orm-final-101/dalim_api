from django.db import models
from django.conf import settings
from config.constants import COURSE_CHOICES
from multiselectfield import MultiSelectField
from datetime import date


class Race(models.Model):
    title = models.CharField(max_length=100)
    organizer = models.CharField(max_length=100)    # 행사주관사 이름
    description = models.TextField() # 대회 소개글
    start_date = models.DateField() # 대회 시작일
    end_date = models.DateField() # 대회 마감일
    reg_start_date = models.DateField() # 신청접수 시작일
    reg_end_date = models.DateField() # 신청접수 마감일
    courses = MultiSelectField(choices=COURSE_CHOICES) # 대회 코스 복수 선택   
    thumbnail_image = models.ImageField(upload_to="races/thumbnail_images/%Y/%m/%d/", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=100) # 대회 장소
    fees = models.IntegerField(default=0) # 참가비용
    register_url = models.URLField(null=True) # 대회 신청 페이지(외부링크)
    
    def __str__(self):
        return self.title

    def d_day(self):
        today = date.today()
        delta = self.reg_end_date - today
        return delta.days
    
    def reg_status(self):    
        today = date.today()  
        if self.reg_start_date > today:
            return "접수예정"
        elif self.reg_start_date <= today <= self.reg_end_date:
            return "접수중"
        elif self.reg_end_date < today:
            return "접수마감"
        else:
            return "날짜 확인 필요"
         

class RaceFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_races")
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.user} - {self.race}"


class RaceReview(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviewd_races")
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"Review by {self.author.username} on {self.race.title}"