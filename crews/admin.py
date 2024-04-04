from django.contrib import admin
from .models import Crew, CrewFavorite, CrewReview
from accounts.models import JoinedCrew


class JoinedCrewInline(admin.TabularInline):
    model = JoinedCrew
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)
    list_display = ("user", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    list_editable = ("status",)

    actions = ["approve_members", "disapprove_members"]

    def approve_members(self, request, queryset):
        queryset.update(status="member")
    approve_members.short_description = "선택된 멤버 승인"

    def disapprove_members(self, request, queryset):
        queryset.update(status="not_member")
    disapprove_members.short_description = "선택된 멤버 미승인"


class CrewAdmin(admin.ModelAdmin):
    list_display = ("name", "location_city", "location_district", "get_member_count", "get_status_display")
    inlines = [JoinedCrewInline]
    search_fields = ("name", "location_city", "location_district")
    list_filter = ("location_city", "is_opened")
    readonly_fields = ("get_member_count",)

    def get_member_count(self, obj):
        return obj.members.filter(status="member").count()
    get_member_count.short_description = "멤버 수"

    def get_status_display(self, obj):
        return "모집중" if obj.is_opened else "모집마감"
    get_status_display.short_description = "모집상태"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["is_opened"].label = "모집여부"
        return form


admin.site.register(Crew, CrewAdmin)
admin.site.register(CrewFavorite)
admin.site.register(CrewReview)