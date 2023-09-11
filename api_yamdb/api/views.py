from rest_framework import viewsets


from reviews.models import Title, Category
from .serializers import (TitleSerializer,
                          CategorySerializer)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
