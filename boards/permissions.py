from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모두에게 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기 권한은 작성자에게만 허용
        return obj.author == request.user


# 일반 사용자는 post_classification의 event, notice 글 작성 불가합니다.
class IsStaffOrGeneralClassification(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            post_classification = request.data.get("post_classification")
            if post_classification in ["event", "notice"]:
                return request.user.is_staff
        return True