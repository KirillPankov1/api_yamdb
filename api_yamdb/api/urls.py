from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import CategoriesViewSet, TitleViewSet

router_v1 = DefaultRouter()
router_v1.register('categories', CategoriesViewSet, basename='categories')
router_v1.register('title', TitleViewSet, basename='title')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/api-token-auth/', views.obtain_auth_token),
    path('v1/', include('djoser.urls.jwt')),

]
