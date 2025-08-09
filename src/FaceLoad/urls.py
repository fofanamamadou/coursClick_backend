"""
URL configuration for FaceLoad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from tkinter.font import names

from django.contrib import admin
from django.urls import path, include

from .settings import DEBUG,MEDIA_URL,MEDIA_ROOT

from django.conf.urls.static import static




from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Les Endpoints pour les API
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("absences.urls")),
    path("api/v1/", include("filiere.urls")),
    path("api/v1/", include("classe.urls")),
    path("api/v1/", include("module.urls")),
    path("api/v1/", include("horaire.urls")),

    path("api/v1/", include("role.urls")),
    path("api/v1/", include("planning.urls")),
    path("api/v1/", include("pointage.urls")),


    # Token
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Ajouter cette ligne pour servir les fichiers image
if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
