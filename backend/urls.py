from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Tailored Remedy API",
        default_version='v1',
        description="A Medical Management and tracking system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('admin/', admin.site.urls),    
    path('api/auth/', include('apps.accounts.api.urls')),
    path('doc/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('doc/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]