from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Promotion, PromotionArticle
from .serializers import PromotionSerializer, PromotionArticleSerializer


@api_view(['GET'])
def promotion_main(request):
    # is_show가 true인 Promotion만 가져오기
    promotions = Promotion.objects.filter(is_show=True)
    serializer = PromotionSerializer(promotions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def promotion_post(request):
    # is_show가 true인 Promotion Article 최근 3개만 가져오기
    promotion_articles = PromotionArticle.objects.filter(is_show=True).order_by('-updated_at')[:3]
    serializer = PromotionArticleSerializer(promotion_articles, many=True)
    return Response(serializer.data)