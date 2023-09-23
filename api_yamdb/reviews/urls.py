from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet)
router.register(r'comments', views.CommentViewSet)

app_name = 'reviews'

urlpatterns = [
    path('', include(router.urls)),
]
