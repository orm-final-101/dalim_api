from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .models import CustomUser, Record, JoinedCrew, JoinedRace
from crews.models import CrewReview
from crews.serializers import CrewListSerializer, ProfileCrewReviewSerializer
from races.models import Race, RaceReview
from races.serializers import RaceListSerializer, ProfileRaceReviewSerializer
from boards.models import Post, Comment, Like
from boards.serializers import (
    PostListSerializer,
    ProfileCommentSerializer,
    ProfileLikedPostSerializer
)
from .serializers import (
    ProfileSerializer,
    RecordSerialiser,
    JoinedCrewSerializer,
    JoinedRaceGetSerializer,
    JoinedRacePostSerializer,
    OpenProfileSerializer
)


# mypage/info는 일단 fbv로 작업 - 완
@extend_schema(
    methods=["PATCH"],
    request=ProfileSerializer
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def mypage_info(request):
    try:
        user = CustomUser.objects.get(pk=request.user.pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
    if request.method == "GET":
        user = CustomUser.objects.get(pk=request.user.pk)
        serializer = ProfileSerializer(user)
        return Response(serializer.data)
    elif request.method == "PATCH":
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    raise MethodNotAllowed(request.method)
     

# mypage/record CRUD는 뷰셋으로 작업 - 완
@extend_schema(
    methods=["POST", "PATCH"],
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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mypage_crew(request):
    try:
        user = CustomUser.objects.get(pk=request.user.pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if request.method == "GET":
        joined_crews = JoinedCrew.objects.filter(user=user)
        serializer = JoinedCrewSerializer(joined_crews, many=True)
        return Response(serializer.data)


# /mypage/race 내가 신청한 대회 내역 : GET, POST
# /mypage/race/<int:joined_race_id> 내 대회 기록 : PATCH, DELETE
@extend_schema(
    methods=["GET", "POST", "PATCH", "DELETE"]
)
class RaceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = JoinedRace.objects.filter(user=request.user)
        serializer = JoinedRaceGetSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=inline_serializer(
            name="RaceCreateInlineSerializer", 
            fields={
                "race_id": serializers.IntegerField()
            }
        )
    )
    def create(self, request):
        race_id = request.data.get("race_id")

        try :
            race = Race.objects.get(pk=race_id)
        except :
            # 해당하는 race 없을 시 에러메세지 반환
            return Response({"error":"해당 대회가 존재하지 않습니다."}, status=404)
        
        # request.user.pk와 race.id를 이용해 JoinedRace 객체를 생성
        data = {
            "user": request.user.pk,
            "race" : race.id
        }

        # 이미 user와 race가 같은 객체가 있는지 확인
        if JoinedRace.objects.filter(user=data["user"], race=data["race"]).exists():
            return Response({"error":"이미 참가한 대회입니다."}, status=400)

        serializer = JoinedRacePostSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    @extend_schema(
        request=inline_serializer(
            name="RaceUpdateInlineSerializer", 
            fields={
                "race_record": serializers.CharField()
            }
        )
    )
    def partial_update(self, request, pk):
        race_record = request.data.get("race_record")

        try:
            joined_race = JoinedRace.objects.get(pk=pk, user=request.user)
        except JoinedRace.DoesNotExist:
            return Response({"error": "해당 JoinedRace가 존재하지 않습니다."}, status=404)
        
        serializer = JoinedRacePostSerializer(joined_race, data={"race_record":race_record}, partial=True)
        if serializer.is_valid():
            serializer.save()            
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def destroy(self, request, pk):
        try:
            joined_race = JoinedRace.objects.get(pk=pk, user=request.user)
        except JoinedRace.DoesNotExist:
            return Response({"error": "해당 JoinedRace가 존재하지 않습니다."}, status=404)
        
        joined_race.delete()
        return Response(status=204)
        
    
# /mypage/favorites : GET
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mypage_favorites(request):
    try:
        user = CustomUser.objects.get(pk=request.user.pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "사용자를 찾을 수 없습니다."}, status=404)

    if request.method == "GET":
        favorite_crews = [favorite.crew for favorite in user.favorite_crews.all()]
        favorite_races = [favorite.race for favorite in user.favorite_races.all()]

        crew_serializer = CrewListSerializer(favorite_crews, many=True, context={"request": request})
        race_serializer = RaceListSerializer(favorite_races, many=True, context={"request": request})

        respnse_data = {
            "crew": crew_serializer.data,
            "race": race_serializer.data
        }

        return Response(respnse_data)
    
    
    raise MethodNotAllowed(request.method)

# /<int:pk>/profile : GET
@api_view(["GET"])
def profile(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
    user_serializer = OpenProfileSerializer(user)
    post_serializer = PostListSerializer(Post.objects.filter(author=user), many=True)
    comments_serializer = ProfileCommentSerializer(Comment.objects.filter(author=user), many=True)
    crew_review_serializer = ProfileCrewReviewSerializer(CrewReview.objects.filter(author=user), many=True)
    race_review_serializer = ProfileRaceReviewSerializer(RaceReview.objects.filter(author=user), many=True) 
    
    fin_data = {
        "user" : user_serializer.data,
        "posts" : post_serializer.data,
        "comments" : comments_serializer.data,
        "reviews" : {
            "crew" : crew_review_serializer.data,
            "race" : race_review_serializer.data
        }
    }

    # request.user와 pk가 일치하는 경우에만 'likes' 항목을 추가
    if request.user.pk == user.pk:
        liked_post_serializer = ProfileLikedPostSerializer(Like.objects.filter(author=user), many=True)
        fin_data["likes"] = liked_post_serializer.data

    return Response(fin_data)