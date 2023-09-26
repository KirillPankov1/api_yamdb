import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg

from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import (PermissionDenied,
                                       ValidationError,
                                       NotFound)
from rest_framework import (generics,
                            viewsets,
                            permissions,
                            status,
                            pagination,
                            filters)
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Genre, Category, Title, Review, Comment
from .serializers import (GenreSerializer,
                          SignUpSerializer,
                          UserSerializer,
                          CategorySerializer,
                          TitleSerializer,
                          TitleWriteSerializer,
                          ReviewSerializer,
                          CommentSerializer,
                          MyTokenObtainPairSerializer)
from .permissions import (IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin,
                         IsAdminOrSuperUser,
                          IsAdminOrSelf, IsSafeMethod, IsModeratorOrHigher, IsAuthor)
from .utils import send_confirmation_code
from .filters import TitleFilter



User = get_user_model()
logger = logging.getLogger(__name__)


class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)

        email = request.data.get('email')
        username = request.data.get('username')

        email_exists = User.objects.filter(email=email).exists()
        username_exists = User.objects.filter(username=username).exists()

        if email_exists and username_exists:
            return Response({'info': 'User already registered'},
                            status=status.HTTP_200_OK)

        if email_exists or username_exists:
            return Response(
                {'error': 'Either Email or Username already exists'},
                status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            )
            confirmation_code = "1234"
            send_confirmation_code(
                serializer.validated_data['email'], confirmation_code
            )

            return Response(
                serializer.validated_data, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')

        if not username:
            return Response({'error': 'Username is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = MyTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'token': 'Generated-JWT-Token'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'head', 'delete', 'patch']
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    pagination_class = pagination.PageNumberPagination
    lookup_field = 'username'
    permission_classes = [IsAdminOrSuperUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        if search_term is not None:
            queryset = queryset.filter(username__icontains=search_term)
        return queryset


class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrSelf]
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return None
        return user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({'detail': 'Unauthorized'},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


####
#
#Запретить get-запросы
#
###
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "Method 'GET' not allowed."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def get(self, request, *args, **kwargs):
        return Response({"detail": "Method 'GET' not allowed."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
    permission_classes = [IsAdminOrSuperUser | IsSafeMethod]

    def retrieve(self,
                 request,
                 slug=None):
        return Response({"detail": "Method 'GET' not allowed."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related('category').all().order_by('name')
    serializer_class = TitleSerializer
    http_method_names = ['get',
                         'post',
                         'put',
                         'patch',
                         'delete',
                         'head',
                         'options']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrSuperUser | IsSafeMethod]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return TitleWriteSerializer
        return TitleSerializer

    def create(self, request):
        serializer = TitleWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = TitleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {"detail": "Method 'PUT' not allowed for this endpoint."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'head', 'delete', 'patch']
    permission_classes = [IsAuthorOrModeratorOrAdmin | IsSafeMethod]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [IsAuthorOrModeratorOrAdmin]
        return super().get_permissions()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id__pk')
        return Review.objects.filter(title__id=title_id).order_by('pub_date')

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id__pk')
        try:
            title = Title.objects.get(id=title_id)
        except ObjectDoesNotExist:
            raise NotFound("Title not found.")

        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied(
                "You must be authenticated to create a review.")

        if Review.objects.filter(title=title, author=user).exists():
            raise ValidationError("You have already reviewed this title.")

        score = serializer.validated_data.get('score')
        if score < 1 or score > 10:
            raise ValidationError("Review score must be between 1 and 10.")
        serializer.save(author=user, title=title)
        title.update_rating()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    http_method_names = ['get', 'post', 'head', 'delete', 'patch']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review_id = self.kwargs.get('review__pk', None)
        if review_id is not None:
            review = get_object_or_404(Review, pk=review_id)
            comments = Comment.objects.filter(review=review).order_by('id')
            return comments
        return Comment.objects.none().order_by('id')

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthorOrModeratorOrAdmin]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review__pk', None)
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            raise NotFound("Review with the given ID does not exist.")
        user = self.request.user
        serializer.save(review=review, author=user)

    def post(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Authentication credentials were not provided.'},
            status=status.HTTP_401_UNAUTHORIZED)
