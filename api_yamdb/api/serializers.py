from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from reviews.models import Category, Genre, Title, Review, Comment
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError

User = get_user_model()


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_email(self, value):
        if len(value) > 254:
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
        min_length=3,
        max_length=30,
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
        if len(value) > 256:
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
        if len(value) > 50:
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

    def to_representation(self, instance):
        return super().to_representation(instance)


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


# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')

    def validate(self, data):
        return data

    def create(self, validated_data):
        return super().create(validated_data)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role

        return token
