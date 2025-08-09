from django.urls import path
from .views import filiere_view, filiere_detail_view

urlpatterns = [
    path("filieres/", filiere_view ),
    path("filieres/<int:id>", filiere_detail_view)
]