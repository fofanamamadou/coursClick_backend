from django.urls import path
from .views import role_view

urlpatterns = [
    path("roles", role_view ),
    # path("setrole/users/<int:user_pk>/approles/<int:role_pk>", set_role_to_user_view)
]