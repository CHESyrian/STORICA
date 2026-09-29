from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from apps.users.auth_views import StoricaTokenObtainPairView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from django_scalar.views import scalar_viewer

from config.api_router import api_router
from common.views.health import HealthCheckView


urlpatterns = [
    path("admin/", admin.site.urls),

    # ======================================
    # API Apps
    # ======================================
    path("api/", include(api_router.urls)),

    # ======================================
    # Health check (unauthenticated)
    # ======================================
    path(
        "api/health/",
        HealthCheckView.as_view(),
        name="health-check",
    ),

    # ======================================
    # JWT Auth
    # ======================================
    path(
        "api/token/",         
        StoricaTokenObtainPairView.as_view(), 
        name="token_obtain_pair"
    ),
    path(  
        "api/token/refresh/", 
        TokenRefreshView.as_view(),    
        name="token_refresh"
    ),
    path(
        "api/token/verify/",  
        TokenVerifyView.as_view(),     
        name="token_verify"
    ),

    # ======================================
    # OpenAPI Schema
    # ======================================
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    # ======================================
    # SCALAR UI
    # ======================================
    path(
        "api/docs/",
        scalar_viewer,
        name="scalar-docs",
    ),
    
]