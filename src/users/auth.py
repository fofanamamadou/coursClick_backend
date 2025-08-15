from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth.models import User as DjangoUser
from .models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    """
    Authentification JWT personnalisée pour le système de gestion des présences
    """
    
    def authenticate_credentials(self, validated_token):
        try:
            user = self.get_user(validated_token)
            if not user.is_active:
                raise AuthenticationFailed('Utilisateur inactif.')
            
            return user, validated_token
        except Exception as e:
            logger.error(f"Erreur d'authentification JWT: {str(e)}")
            raise AuthenticationFailed('Token invalide.')

def authenticate_admin(email, password):
    """
    Authentifie un administrateur avec email et mot de passe
    """
    try:
        # Chercher l'utilisateur par email
        user = User.objects.filter(email=email, is_active=True).first()
        
        if not user:
            return None
            
        # Vérifier que c'est bien un admin
        if not (user.is_staff or user.is_superuser):
            return None
            
        # Vérifier le mot de passe
        if user.check_password(password):
            # Mettre à jour la dernière connexion
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return {
                'user': user,
                'user_type': 'superuser' if user.is_superuser else 'admin'
            }
        else:
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors de l'authentification admin: {str(e)}")
        return None

def authenticate_user(email, password):
    """
    Authentifie un utilisateur (professeur ou étudiant) avec email et mot de passe
    """
    try:
        # Chercher l'utilisateur par email
        user = User.objects.filter(email=email, is_active=True).first()
        
        if not user:
            return None
            
        # Vérifier que ce n'est pas un admin
        if user.is_staff or user.is_superuser:
            return None
            
        # Vérifier le mot de passe
        if user.check_password(password):
            # Mettre à jour la dernière connexion
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Déterminer le type d'utilisateur
            user_roles = [role.name for role in user.roles.all()]
            
            if 'PROFESSOR' in user_roles:
                user_type = 'professor'
            elif 'STUDENT' in user_roles:
                user_type = 'student'
            else:
                user_type = 'user'
            
            return {
                'user': user,
                'user_type': user_type,
                'roles': user_roles
            }
        else:
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors de l'authentification utilisateur: {str(e)}")
        return None

def generate_tokens(user):
    """
    Génère les tokens JWT pour un utilisateur
    """
    try:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 86400  # 24 heures en secondes
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération des tokens: {str(e)}")
        return None

def get_user_permissions(user):
    """
    Récupère les permissions d'un utilisateur selon son rôle
    """
    permissions = {
        'is_admin': user.is_staff or user.is_superuser,
        'is_superuser': user.is_superuser,
        'is_professor': False,
        'is_student': False,
        'can_manage_users': user.is_staff or user.is_superuser,
        'can_view_planning': False,
        'can_create_planning': False,
        'can_manage_absences': False,
        'can_view_statistics': False
    }
    
    # Permissions spécifiques selon les rôles
    user_roles = [role.name for role in user.roles.all()]
    
    if 'PROFESSOR' in user_roles:
        permissions.update({
            'is_professor': True,
            'can_view_planning': True,
            'can_create_planning': True,
            'can_manage_absences': True,
            'can_view_statistics': True
        })
    elif 'STUDENT' in user_roles:
        permissions.update({
            'is_student': True,
            'can_view_planning': True
        })
    
    # Permissions admin
    if user.is_staff or user.is_superuser:
        permissions.update({
            'can_view_planning': True,
            'can_create_planning': True,
            'can_manage_absences': True,
            'can_view_statistics': True,
            'can_manage_system': True
        })
    
    return permissions

def get_user_from_token(request):
    """
    Récupère l'utilisateur depuis le token JWT dans la requête
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        
        # Décoder le token pour récupérer l'utilisateur
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        
        user = User.objects.get(id=user_id, is_active=True)
        return user
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur depuis le token: {str(e)}")
        return None

def validate_password_strength(password):
    """
    Valide la force d'un mot de passe
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    # Vous pouvez ajouter d'autres règles de validation ici
    return True, "Mot de passe valide"

def can_user_login(user):
    """
    Vérifie si un utilisateur peut se connecter
    """
    if not user.is_active:
        return False, "Votre compte a été désactivé. Veuillez contacter l'administrateur."
    
    # Vous pouvez ajouter d'autres vérifications ici (compte verrouillé, etc.)
    return True, "Connexion autorisée"
