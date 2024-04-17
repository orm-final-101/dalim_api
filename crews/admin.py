from django.contrib import admin
from django.db import models
from .models import Crew, CrewFavorite, CrewReview
from accounts.models import CustomUser, JoinedCrew


"""
JoinedCrewInline 클래스
- 크루 관리자 페이지에서 크루 멤버 관리를 위한 Inline 클래스
- JoinedCrew 모델을 인라인으로 표시
- 생성/수정 시간 필드는 읽기 전용
- 유저 필드는 raw_id_field로 표시되어 검색 가능
- 리스트 디스플레이에 유저, 상태, 생성/수정 시간 표시
- 상태 필드로 필터링 가능
- 유저 이름, 이메일로 검색 가능
- 상태 필드 편집 가능
- 멤버 승인, 거절, 탈퇴 액션 제공
"""
class JoinedCrewInline(admin.TabularInline):
    model = JoinedCrew
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)
    list_display = ("user", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    list_editable = ("status",)

    actions = ["approve_members", "disapprove_members", "quit_members"]

    def approve_members(self, request, queryset):
        queryset.update(status="member")
    approve_members.short_description = "선택된 멤버 승인"

    def disapprove_members(self, request, queryset):
        queryset.update(status="non_keeping")
    disapprove_members.short_description = "선택된 멤버 거절"

    def quit_members(self, request, queryset):
        queryset.update(status="quit")
    quit_members.short_description = "선택된 멤버 탈퇴 처리"


"""
CrewAdmin 클래스

- Crew 모델의 관리자 클래스
- 리스트 디스플레이에 이름, 지역, 멤버 수, 모집 상태 표시
- JoinedCrewInline을 인라인으로 표시
- 이름, 지역으로 검색 가능
- 지역, 모집여부로 필터링 가능
- 멤버 수 필드는 읽기 전용
- 크루 소유자 필드에서 크루 관리자 또는 스탭만 선택 가능
- 모집여부 필드 레이블 변경
"""
class CrewAdmin(admin.ModelAdmin):
    list_display = ("name", "location_city", "location_district", "get_member_count", "get_status_display")
    inlines = [JoinedCrewInline]
    search_fields = ("name", "location_city", "location_district")
    list_filter = ("location_city", "is_opened")
    readonly_fields = ("get_member_count",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = CustomUser.objects.filter(
                models.Q(user_type="crew") | models.Q(is_staff=True)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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


"""
CrewReviewAdmin 클래스

- CrewReview 모델의 관리자 클래스
- 리스트 디스플레이에 작성자, 크루, 생성/수정 시간 표시
- 작성자 이름, 이메일, 크루 이름, 내용으로 검색 가능
- 크루로 필터링 가능
- 작성자, 크루 필드는 raw_id_field로 표시되어 검색 가능
"""
class CrewReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "crew", "created_at", "updated_at")
    search_fields = ("author__username", "author__email", "crew__name", "contents")
    list_filter = ("crew",)
    raw_id_fields = ("author", "crew")


"""
CrewFavoriteAdmin 클래스

- CrewFavorite 모델의 관리자 클래스
- 리스트 디스플레이에 유저, 크루, 생성/수정 시간 표시
- 유저 이름, 이메일, 크루 이름으로 검색 가능
- 크루로 필터링 가능
- 유저, 크루 필드는 raw_id_field로 표시되어 검색 가능
"""
class CrewFavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "crew", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "crew__name")
    list_filter = ("crew",)
    raw_id_fields = ("user", "crew")


# 모델 등록
admin.site.register(Crew, CrewAdmin)
admin.site.register(CrewFavorite, CrewFavoriteAdmin)
admin.site.register(CrewReview, CrewReviewAdmin)