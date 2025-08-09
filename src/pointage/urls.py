from django.urls import path
from .views import CreateSessionPresenceView, ValidatePresenceView, list_presences_view, list_presences_today_view

urlpatterns = [
    path('session/create/', CreateSessionPresenceView.as_view(), name='create-session'),
    path('validate/', ValidatePresenceView.as_view(), name='validate-presence'),
    path('presences/', list_presences_view, name='list-presences'),
    path('presences/today/', list_presences_today_view, name='list-presences-today')

]
