from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Permission qui permet l'accès uniquement aux utilisateurs ayant le rôle 'Admin'.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user and request.user.is_staff




class IsProfessor(permissions.BasePermission):
    """
    Permission qui permet l'accès uniquement aux utilisateurs ayant le rôle 'PROFESSOR'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.roles.filter(name='PROFESSOR').exists()


class IsStudent(permissions.BasePermission):
    """
    Permission qui permet l'accès uniquement aux utilisateurs ayant le rôle 'STUDENT'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.roles.filter(name='STUDENT').exists()

class IsSuperuser(permissions.BasePermission):
    """
    Permission qui permet l'accès uniquement aux superutilisateurs.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsRegularAdmin(permissions.BasePermission):
    """
    Permission qui permet l'accès uniquement aux administrateurs "normaux".
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff and not request.user.is_superuser

class IsAnyAdmin(permissions.BasePermission):
    """
    Permission qui permet l'accès à n'importe quel type d'administrateur.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff