from django.urls import path
from .views import module_view, module_detail_view, get_professor_modules
urlpatterns = [
    path("modules/", module_view),
    path("modules/<int:id>", module_detail_view),
    path('professeurs/<int:professor_id>/modules/', get_professor_modules),

]