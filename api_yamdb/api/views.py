from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

from rest_framework import viewsets


from reviews.models import Title, Category
from .serializers import (TitleSerializer,
                          CategorySerializer)

User = get_user_model()


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
