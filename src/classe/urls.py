from django.urls import path
from .views import classe_view, classe_detail_view
urlpatterns = [
    path('classes', classe_view),
    path("classes/<int:id>", classe_detail_view)
]