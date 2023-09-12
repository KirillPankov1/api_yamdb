from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('redoc/',
         TemplateView.as_view(template_name='redoc.html'),
         name='redoc'),
    path('api/v1/reviews/', include('reviews.urls', namespace='reviews')),
    path('api/v1/', include('api.urls', namespace='api')),
]
