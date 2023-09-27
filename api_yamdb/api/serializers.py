from typing import Any, Dict
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()

NUMBER_OF_VALUES = 254
MIN_USER_NAME = 3
MAX_USER_NAME = 30
LEN_NAME = 256
LEN_NAME_SLUG = 50


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_email(self, value):
        if len(value) > NUMBER_OF_VALUES:
            raise serializers.ValidationError(
                'Email should not be longer than 254 characters.')
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

    def update(self, instance, validated_data):
        # Проверка на роль пользователя, который делает запрос
        request = self.context.get('request')
        if request and request.user.role != 'admin':
            validated_data.pop('role', None)
            # Удаление поля role, если оно есть

        return super(UserSerializer, self).update(instance, validated_data)


# SignUp Serializer
class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(
        min_length=MIN_USER_NAME,
        max_length=MAX_USER_NAME,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9_]+$',
                'Username must contain only '
                'alphanumeric characters and underscores.'
            )
        ]
    )


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')

    def validate_name(self, value):
        if len(value) > LEN_NAME:
            raise ValidationError(
                'Category name should not exceed 256 characters.')
        return value


class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


# Genre Serializer
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')

    def validate_slug(self, value):
        if len(value) > LEN_NAME_SLUG:
            raise ValidationError(
                'Genre slug should not exceed 50 characters.')
        return value


# Title Serializer
class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')

    def validate(self, data):
        if 'name' not in data:
            raise serializers.ValidationError(
                {"name": "This field is required."})

        return data


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True)
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id__pk')
            title = get_object_or_404(Title, id=title_id)        
            author = self.context['request'].user
            if Review.objects.filter(title = title, author = author).exists():
                raise ValidationError()
        return super().validate(attrs)
    



# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        return token
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        username = attrs.get('username')
        get_object_or_404(User, username = username)
        return super().validate(attrs)