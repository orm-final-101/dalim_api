from rest_framework import permissions

class IsStaffOrGeneralClassification(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            post_classification = request.data.get('post_classification')
            if post_classification in ['event', 'notice']:
                return request.user.is_staff
        return True