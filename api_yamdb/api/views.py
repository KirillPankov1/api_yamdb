from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from .models import Comment, Review, Title, Category
from .serializers import (TitleSerializer, CategorySerializer,
                          CommentSerializer, ReviewSerializer)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_review(self):
        return (get_object_or_404(Review, id=self.kwargs.get('review_id')))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_titles(self):
        return (get_object_or_404(Title, id=self.kwargs.get('titles_id')))

    def get_queryset(self):
        return self.get_titles().review.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, titles=self.get_titles())
