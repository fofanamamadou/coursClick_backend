from django.urls import path, include
from .views import (
    users_view,
    users_details_view,
    disable_user_view,
    list_students,
    list_admins,
    list_professors,
    create_admin_view
)
from .auth_views import (
    admin_login_view,
    user_login_view,
    profile_view,
    logout_view,
    refresh_token_view,
    change_password_view,
    forgot_password_view,
    reset_password_view as auth_reset_password_view
)



# Nouveaux patterns d'authentification
auth_patterns = [
    path('admin/login/', admin_login_view, name='auth_admin_login'),
    path('user/login/', user_login_view, name='auth_user_login'),
    path('logout/', logout_view, name='auth_logout'),
    path('refresh/', refresh_token_view, name='auth_refresh'),
    path('profile/', profile_view, name='auth_profile'),
    path('change-password/', change_password_view, name='auth_change_password'),
    path('forgot-password/', forgot_password_view, name='auth_forgot_password'),
    path('reset-password/', auth_reset_password_view, name='auth_reset_password'),
]

urlpatterns = [
    # URLs d'authentification
    path('auth/', include(auth_patterns)),

    # URLs pour la gestion des utilisateurs
    path("users/", users_view),
    path("users/students/", list_students),
    path("users/admins/", list_admins),
    path("users/professors/", list_professors),
    path("users/<int:id>/", users_details_view),
    path("users/create-admin/", create_admin_view),
    path("users/<int:user_pk>/disable/", disable_user_view),
]
