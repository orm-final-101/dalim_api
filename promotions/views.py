from rest_framework.response import Response
from rest_framework import viewsets
from .models import Promotion, PromotionArticle
from .serializers import PromotionSerializer, PromotionArticleSerializer


class ListOnlyViewSet(
    viewsets.GenericViewSet
):  # list만 보이는 뷰셋 만들어 공통으로 상속
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PromotionViewSet(ListOnlyViewSet):
    serializer_class = PromotionSerializer
    queryset = Promotion.objects.filter(is_show=True)


class PromotionArticleViewSet(ListOnlyViewSet):
    serializer_class = PromotionArticleSerializer
    queryset = PromotionArticle.objects.filter(is_show=True).order_by("-updated_at")[:3]
