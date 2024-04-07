from rest_framework.response import Response
from rest_framework import viewsets
from django.conf import settings
from .serializers import CustomUserSerializer, ProfileSerializer
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from .models import CustomUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.openapi import OpenApiParameter


# mypage/info는 일단 fbv로 작업 - 완
@extend_schema(
    methods=['PATCH'],
    request=ProfileSerializer
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def mypage_info(request):
    try:
        user = CustomUser.objects.get(pk=request.user.pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
    if request.method == 'GET':
        user = CustomUser.objects.get(pk=request.user.pk)
        serializer = ProfileSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    raise MethodNotAllowed(request.method)
     

# mypage/record CRUD는 뷰셋으로 작업
class RecordViewSet(viewsets.ViewSet):
    pass

# /mypage/crew 내가 신청한 크루 현황

# /mypage/race 내가 신청한 대회 내역 : GET, POST

# /mypage/race/record/<int:race_id> : POST, PATCH, DELETE

# /mypage/favorites : GET

# /<int:pk>/profile : GET

# /accounts/<int:pk>/likes : GET (본인만)

# /accounts/<int:pk>/reviews