from django.contrib import admin
from django.db.models import Sum
from .models import LevelStep, JoinedCrew, JoinedRace, Record, CustomUser


class JoinedCrewInline(admin.TabularInline):
    model = JoinedCrew
    extra = 0
    readonly_fields = ("created_at", "updated_at")


class JoinedRaceInline(admin.TabularInline):
    model = JoinedRace
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    

class RecordInline(admin.TabularInline):
    model = Record
    extra = 0


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "user_type", "is_staff", "total_distance")
    inlines = [JoinedCrewInline, JoinedRaceInline, RecordInline]
    readonly_fields = ("total_distance",)

    def total_distance(self, obj):
        return obj.records.aggregate(total_distance=Sum('distance'))['total_distance'] or 0
    total_distance.short_description = 'Total Distance'


admin.site.register(LevelStep)
admin.site.register(Record)
admin.site.register(CustomUser, CustomUserAdmin)