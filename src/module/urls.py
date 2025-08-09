from django.urls import path
from .views import module_view, module_detail_view
urlpatterns = [
    path("modules", module_view),
    path("modules/<int:id>", module_detail_view)

]