from rest_framework import permissions
from accounts.models import JoinedCrew


class IsCrewMember(permissions.BasePermission):
    def has_permission(self, request, view):
        crew_id = view.kwargs.get("crew_id")
        user = request.user

        if user.is_authenticated:
            if user.is_superuser or user.role == "crew":
                return True
            else:
                return JoinedCrew.objects.filter(
                    user=user, crew_id=crew_id, status__in=["member", "quit"]
                ).exists()

        return False