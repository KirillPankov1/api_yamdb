from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from .models import Comment, Review


class CommentSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ['user', 'review']


class ReviewSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ['user', 'titles']