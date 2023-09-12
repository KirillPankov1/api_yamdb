from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'titles', views.TitleViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'categories', views.CategoryViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('auth/token/', views.TokenView.as_view(), name='token'),
]
