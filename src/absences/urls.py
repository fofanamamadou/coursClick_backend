from django.urls import path
from .views import (
    GenererAbsencesView,
    StudentAbsenceViewSet,
    AdminAbsenceViewSet
)

urlpatterns = [
    # URL pour la génération automatique des absences
    path('absences/generate/', GenererAbsencesView.as_view(), name='generate-absences'),

    # URLs pour les étudiants concernant leurs absences
    path(
        'absences/my-absences/',
        StudentAbsenceViewSet.as_view({'get': 'list'}),
        name='student-absence-list'
    ),
    path(
        'absences/my-absences/<int:pk>/',
        StudentAbsenceViewSet.as_view({'get': 'retrieve'}),
        name='student-absence-detail'
    ),
    path(
        'absences/my-absences/<int:pk>/justifier/',
        StudentAbsenceViewSet.as_view({'post': 'justifier', 'put': 'justifier'}),
        name='student-absence-justify'
    ),

    # URLs pour les administrateurs pour gérer les absences
    path(
        'absences/manage-absences/',
        AdminAbsenceViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='admin-absence-list-create'
    ),
    path(
        'absences/manage-absences/<int:pk>/',
        AdminAbsenceViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='admin-absence-detail-update-delete'
    ),
    path(
        'absences/manage-absences/<int:pk>/approuver/',
        AdminAbsenceViewSet.as_view({'post': 'approuver'}),
        name='admin-absence-approve'
    ),
    path(
        'absences/manage-absences/<int:pk>/refuser/',
        AdminAbsenceViewSet.as_view({'post': 'refuser'}),
        name='admin-absence-refuse'
    ),
]