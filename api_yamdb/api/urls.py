from django.urls import path, include

from rest_framework_nested.routers import DefaultRouter
from rest_framework_nested import routers

from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'titles', views.TitleViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'categories', views.CategoryViewSet)


titles_router = routers.NestedSimpleRouter(router,
                                           r'titles',
                                           lookup='title_id')
titles_router.register(r'reviews',
                       views.ReviewViewSet,
                       basename='title-reviews')
reviews_router = routers.NestedSimpleRouter(titles_router,
                                            r'reviews',
                                            lookup='review')
reviews_router.register(r'comments',
                        views.CommentViewSet,
                        basename='review-comments')

app_name = 'api'

urlpatterns = [
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/token/', views.TokenView.as_view(), name='token'),
    path('admin/users/',
         views.AdminCreateUserView.as_view(),
         name='admin_create_user'),
    path('users/me/', views.CurrentUserView.as_view(), name='current_user'),
    path('', include(router.urls)),
    path('', include(titles_router.urls)),
    path('', include(reviews_router.urls)),
]
