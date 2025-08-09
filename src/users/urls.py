from django.urls import path
from .views import users_view
from .views import users_details_view
from .views import disable_user_view
from .views import update_password_view
from .views import reset_password_view, list_students, list_personnels, list_admins, list_professors, create_admin_view, get_professor_modules, CustomTokenObtainPairView


urlpatterns = [
    path("users", users_view),
    path("users/students", list_students),
    path("users/personnels", list_personnels),
    path("users/admins", list_admins),
    path("users/professors", list_professors),
    path("users/<int:id>", users_details_view),
    path("users/create-admin", create_admin_view),
    path("users/<int:user_pk>/disable", disable_user_view),
    path("change-password", update_password_view),
    path("reset-password", reset_password_view),
    path('professeurs/<int:professor_id>/modules/', get_professor_modules),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
