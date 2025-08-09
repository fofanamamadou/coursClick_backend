from django.urls import path
from .views import planning_view, planning_detail_view, valider_cours, get_user_plannings, validateCoursByAdmin

urlpatterns = [
    path("plannings", planning_view),
    path("plannings/<int:id>", planning_detail_view),
    path("plannings/valider/<int:id>", valider_cours),
    path("plannings/admin/valider/<int:id>/", validateCoursByAdmin),
    path("plannings/professeurOnline", get_user_plannings),

]