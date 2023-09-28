import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import (viewsets,
                            permissions,
                            status,
                            pagination,
                            filters,
                            mixins)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Genre, Category, Title, Review, Comment

from .serializers import (
    GenreSerializer,
    SignUpSerializer,
    UserSerializer,
    CategorySerializer,
    TitleSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer,
    MyTokenObtainPairSerializer,)
from .permissions import (
    IsAuthorOrModeratorOrAdmin,
    IsAdminOrSuperUser,
    IsSafeMethod,)
from .utils import send_confirmation_code
from .filters import TitleFilter


User = get_user_model()
logger = logging.getLogger(__name__)


class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if 'user' in serializer.validated_data:
            user = serializer.validated_data.get('user')
            serializer.validated_data.pop('user')
        else:
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'])
        try:
            send_confirmation_code(
                serializer.validated_data['email'], user.confirmation_code
            )
        except Exception:
            pass

        return Response(
            serializer.validated_data, status=status.HTTP_200_OK
        )


class TokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(User, username=username)
        serializer = MyTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            'token': 'Generated-JWT-Token'}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'head', 'delete', 'patch']
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    pagination_class = pagination.PageNumberPagination
    lookup_field = 'username'
    permission_classes = [permissions.IsAuthenticated & IsAdminOrSuperUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)

    @action(detail=False,
            methods=['patch', 'get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request, pk=None):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = self.get_serializer(request.user,
                                             data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class CreateDeleteListViewSet(mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    pass


class CategoryViewSet(CreateDeleteListViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsSafeMethod | (permissions.IsAuthenticated & IsAdminOrSuperUser)]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class GenreViewSet(CreateDeleteListViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
    permission_classes = [IsSafeMethod | (permissions.IsAuthenticated & IsAdminOrSuperUser)]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related('category').all().order_by('name')
    serializer_class = TitleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    permission_classes = [IsSafeMethod | (permissions.IsAuthenticated & IsAdminOrSuperUser)]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return TitleWriteSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'delete', 'patch']
    filter_backends = [DjangoFilterBackend, ]
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsSafeMethod]
        else:
            self.permission_classes = [IsAuthorOrModeratorOrAdmin]
        return super().get_permissions()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id__pk')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all().order_by('id',)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id__pk')
        title = get_object_or_404(Title, id=title_id)
        user = self.request.user
        serializer.save(author=user, title=title)
        title.update_rating()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    http_method_names = ['get', 'post', 'delete', 'patch']
    filter_backends = [DjangoFilterBackend, ]
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [IsSafeMethod]
        else:
            self.permission_classes = [IsAuthorOrModeratorOrAdmin]
        return super().get_permissions()

    def get_queryset(self):
        review_id = self.kwargs.get('review__pk', None)
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all().order_by('id',)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review__pk', None)
        review = get_object_or_404(Review, pk=review_id)
        user = self.request.user
        serializer.save(review=review, author=user)
