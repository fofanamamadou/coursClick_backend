from django.urls import path
from .views import planning_view, planning_detail_view, valider_cours, get_user_plannings, validateCoursByAdmin, get_plannings_by_date, get_plannings_by_user, get_plannings_by_module, get_validated_plannings_by_professor, get_pending_plannings, get_planning_stats, get_plannings_by_date_range, get_today_plannings, get_week_plannings, reset_planning_validation, get_professor_week_schedule

urlpatterns = [
    path("plannings", planning_view),
    path("plannings/<int:id>", planning_detail_view),
    path("plannings/valider/<int:id>", valider_cours),
    path("plannings/admin/valider/<int:id>/", validateCoursByAdmin),
    path("plannings/professeurOnline", get_user_plannings),
    path("plannings/by-date/", get_plannings_by_date),  # ?date=YYYY-MM-DD
    path("plannings/by-user/<int:user_id>/", get_plannings_by_user),
    path("plannings/by-module/<int:module_id>/", get_plannings_by_module),
    path("plannings/validated-by-professor/", get_validated_plannings_by_professor),
    path("plannings/pending/", get_pending_plannings),
    path("plannings/stats/", get_planning_stats),
    path("plannings/date-range/", get_plannings_by_date_range),  # ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    path("plannings/today/", get_today_plannings),
    path("plannings/week/", get_week_plannings),
    path("plannings/reset/<int:id>/", reset_planning_validation),
    path("plannings/professor/week-schedule/", get_professor_week_schedule),


]