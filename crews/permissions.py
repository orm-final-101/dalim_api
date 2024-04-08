from rest_framework import permissions
from accounts.models import JoinedCrew

class IsCrewOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsCrewAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == "crew"

class IsCrewMemberOrQuit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return JoinedCrew.objects.filter(user=user, crew=obj, status__in=["member", "quit"]).exists()