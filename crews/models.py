from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField
from config.constants import LOCATION_CITY_CHOICES


MEET_DAY_CHOICES = (
    ("mon", "월"),
    ("tue", "화"),
    ("wed", "수"),
    ("thu", "목"),
    ("fri", "금"),
    ("sat", "토"),
    ("sun", "일"),
)

TIME_CHOICES = [
    (f"{hour:02d}:{minute:02d} {'AM' if hour < 12 else 'PM'}", f"{hour % 12 or 12:02d}:{minute:02d} {'AM' if hour < 12 else 'PM'}")
    for hour in range(24)
    for minute in (0, 30)
]

class Crew(models.Model):
    name = models.CharField(max_length=50)
    location_city = models.CharField(max_length=100, choices=LOCATION_CITY_CHOICES)
    location_district = models.CharField(max_length=100)
    meet_days = MultiSelectField(choices=MEET_DAY_CHOICES)
    meet_time = models.CharField(max_length=10, choices=TIME_CHOICES)
    description = models.TextField("")
    thumbnail_image = models.ImageField(upload_to="crews/thumbnail/%Y/%m/%d/", blank=True, null=True)
    sns_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    def is_favorite(self, user):
        return CrewFavorite.objects.filter(user=user, crew=self).exists()


class CrewFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_crews")
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.crew.name}"


class CrewReview(models.Model):
    crew = models.ForeignKey(Crew, related_name="reviews", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.author.username} on {self.crew.name}"