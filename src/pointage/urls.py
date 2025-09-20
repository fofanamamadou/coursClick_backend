from django.urls import path
from .views import (
    CreateSessionPresenceView, 
    ValidatePresenceView, 
    PointageListView, 
    list_presences_today_view,
    StudentPointageHistoryView
)

urlpatterns = [
    path('session/create/', CreateSessionPresenceView.as_view(), name='create-session'),
    path('validate/', ValidatePresenceView.as_view(), name='validate-presence'),
    path('presences/', PointageListView.as_view(), name='list-presences'),
    path('presences/today/', list_presences_today_view, name='list-presences-today'),
    path('my-history-pointage/', StudentPointageHistoryView.as_view(), name='student-pointage-history'),

]
