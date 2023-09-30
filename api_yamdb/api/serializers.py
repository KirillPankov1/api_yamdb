from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api_yamdb.settings import LEN_MAX, NUMBER_OF_VALUES
from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()

MIN_USER_NAME = 3
MAX_USER_NAME = 30


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(required=True, max_length=NUMBER_OF_VALUES)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.role != User.Roles.ADMIN:
            validated_data.pop('role', None)
        return super(UserSerializer, self).update(instance, validated_data)


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

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        email_exists = User.objects.filter(email=email).exists()
        username_exists = User.objects.filter(username=username).exists()
        if not (email_exists and username_exists):
            if email_exists or username_exists:
                raise ValidationError(
                    'Invalid data:email or username already in use')
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=LEN_MAX)

    class Meta:
        model = Category
        fields = ('name', 'slug')


class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True)
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


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
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError('Вы не можете добавить более одного',
                                      'отзыва на произведение')
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        super().validate(attrs)
        user = get_object_or_404(User, username=attrs.get('username'))
        if user.confirmation_code != attrs.get('confirmation_code'):
            raise ValidationError('Invalid confirmation code')
