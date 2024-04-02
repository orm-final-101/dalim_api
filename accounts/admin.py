from django.contrib import admin
from .models import LevelStep, JoinedCrew, JoinedRace, Record, CustomUser

admin.site.register(LevelStep)
admin.site.register(JoinedCrew)
admin.site.register(JoinedRace)
admin.site.register(Record)
admin.site.register(CustomUser)