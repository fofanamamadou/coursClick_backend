from django.urls import path

from .views import horaire_view, horaire_detail_view, horaires_par_module, horaires_professeur_view, horaires_etudiant_view

urlpatterns=[
    path("horaires", horaire_view),
    path("horaires/<int:id>", horaire_detail_view),
    path('horaires/module/<int:module_id>/', horaires_par_module),
    path('horaires/professeur/', horaires_professeur_view),
    path('horaires/etudiant/', horaires_etudiant_view)
]