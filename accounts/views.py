from rest_framework.response import Response
from rest_framework import viewsets
from django.conf import settings
from .serializers import ProfileSerializer, RecordSerialiser, JoinedCrewSerializer
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from .models import CustomUser, Record, JoinedCrew
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
     

# mypage/record CRUD는 뷰셋으로 작업 - 완
@extend_schema(
    methods=['POST', 'PATCH'],
    request=RecordSerialiser
)
class RecordViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Record.objects.filter(user=request.user)
        serializer = RecordSerialiser(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = RecordSerialiser(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            record = Record.objects.get(pk=pk, user=request.user)
        except Record.DoesNotExist:
            return Response({"error": "Record not found"}, status=404)
        
        serializer = RecordSerialiser(record)
        return Response(serializer.data)
    
    def partial_update(self, request, pk=None):
        try:
            record = Record.objects.get(pk=pk, user=request.user)
        except Record.DoesNotExist:
            return Response({"error": "Record not found"}, status=404)
        
        serializer = RecordSerialiser(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def destroy(self, request, pk=None):
        try:
            record = Record.objects.get(pk=pk, user=request.user)
        except Record.DoesNotExist:
            return Response({"error": "Record not found"}, status=404)
        
        record.delete()
        return Response(status=204)


# /mypage/crew 내가 신청한 크루 현황
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mypage_crew(request):
    try:
        user = CustomUser.objects.get(pk=request.user.pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if request.method == 'GET':
        joined_crews = JoinedCrew.objects.filter(user=user)
        serializer = JoinedCrewSerializer(joined_crews, many=True)
        return Response(serializer.data)

# /mypage/race 내가 신청한 대회 내역 : GET, POST

# /mypage/race/record/<int:race_id> : POST, PATCH, DELETE

# /mypage/favorites : GET

# /<int:pk>/profile : GET

# /accounts/<int:pk>/likes : GET (본인만)

# /accounts/<int:pk>/reviews