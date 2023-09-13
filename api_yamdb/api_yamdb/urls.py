from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('redoc/',
         TemplateView.as_view(template_name='redoc.html'),
         name='redoc'),
    path('api/v1/reviews/', include('reviews.urls', namespace='reviews')),
    path('api/v1/', include('api.urls', namespace='api')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
