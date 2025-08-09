from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GenererAbsencesView,
    StudentAbsenceViewSet,
    AdminAbsenceViewSet
)

# Création d'un routeur pour gérer automatiquement les URLs des ViewSets
router = DefaultRouter()

# Enregistrement des ViewSets auprès du routeur
# Le `basename` est important quand le queryset est dynamique
router.register(r'my-absences', StudentAbsenceViewSet, basename='student-absence')
router.register(r'manage-absences', AdminAbsenceViewSet, basename='admin-absence')

urlpatterns = [
    # URL pour la génération automatique des absences
    path('absences/generate/', GenererAbsencesView.as_view(), name='generate-absences'),
    
    # Inclure les URLs générées par le routeur
    path('absences/', include(router.urls)),
]

# Les URLs générées par le routeur seront :
# /api/absences/my-absences/ -> Liste des absences de l'étudiant (GET)
# /api/absences/my-absences/{id}/ -> Détail d'une absence (GET)
# /api/absences/my-absences/{id}/justifier/ -> Justifier une absence (POST, PUT)
# 
# /api/absences/manage-absences/ -> Liste de toutes les absences pour l'admin (GET, POST)
# /api/absences/manage-absences/{id}/ -> Gérer une absence (GET, PUT, DELETE)
# /api/absences/manage-absences/{id}/approuver/ -> Approuver (POST)
# /api/absences/manage-absences/{id}/refuser/ -> Refuser (POST)
