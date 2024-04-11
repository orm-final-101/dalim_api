from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField
from config.constants import LOCATION_CITY_CHOICES, MEET_DAY_CHOICES, TIME_CHOICES


class Crew(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_crews")
    name = models.CharField(max_length=50)
    location_city = models.CharField(max_length=100, choices=LOCATION_CITY_CHOICES)
    location_district = models.CharField(max_length=100)
    meet_days = MultiSelectField(choices=MEET_DAY_CHOICES)
    meet_time = models.CharField(max_length=10, choices=TIME_CHOICES)
    description = models.TextField("")
    thumbnail_image = models.ImageField(upload_to="crews/thumbnail/%Y/%m/%d/", null=True)
    sns_link = models.URLField(null=True)
    is_opened = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def is_favorite(self, user):
        return CrewFavorite.objects.filter(user=user, crew=self).exists()
    
    def get_status_display(self):
        return "모집중" if self.is_opened else "모집마감"


class CrewFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_crews")
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.crew.name}"


class CrewReview(models.Model):
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviewd_crews")
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.author.username} on {self.crew.name}"