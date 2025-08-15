from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer
from .auth import (
    authenticate_admin, 
    authenticate_user, 
    generate_tokens, 
    get_user_permissions,
    get_user_from_token,
    validate_password_strength,
    can_user_login
)
import json
import logging
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import password_reset_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils import timezone

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login_view(request):
    """
    Vue de connexion spécifique pour les administrateurs (superusers et staff)
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authentifier l'administrateur
        auth_result = authenticate_admin(email, password)
        
        if auth_result:
            user = auth_result['user']
            user_type = auth_result['user_type']
            
            # Générer les tokens JWT
            tokens = generate_tokens(user)
            if not tokens:
                return Response({
                    'error': 'Erreur lors de la génération des tokens'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Récupérer les permissions
            permissions = get_user_permissions(user)
            
            response_data = {
                'success': True,
                'message': 'Connexion administrateur réussie',
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'user_type': user_type,
                'permissions': permissions,
                'token_type': tokens['token_type'],
                'expires_in': tokens['expires_in'],
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_superuser': user.is_superuser,
                    'is_staff': user.is_staff,
                    'last_login': user.last_login,
                    'date_joined': user.date_joined
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Email ou mot de passe incorrect pour l\'administrateur'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Données JSON invalides'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erreur lors de la connexion admin: {str(e)}")
        return Response({
            'error': 'Erreur lors de la connexion'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login_view(request):
    """
    Vue de connexion commune pour les professeurs et étudiants
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si l'utilisateur existe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Vérifier si le compte peut se connecter
        can_login, message = can_user_login(user)
        if not can_login:
            return Response({
                'error': message
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Authentifier l'utilisateur
        auth_result = authenticate_user(email, password)
        
        if auth_result:
            user = auth_result['user']
            user_type = auth_result['user_type']
            roles = auth_result['roles']
            
            # Générer les tokens JWT
            tokens = generate_tokens(user)
            if not tokens:
                return Response({
                    'error': 'Erreur lors de la génération des tokens'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Récupérer les permissions
            permissions = get_user_permissions(user)
            
            # Sérialiser les données de l'utilisateur
            serializer = UserSerializer(user)
            
            response_data = {
                'success': True,
                'message': f'Connexion {user_type} réussie',
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'user_type': user_type,
                'roles': roles,
                'permissions': permissions,
                'token_type': tokens['token_type'],
                'expires_in': tokens['expires_in'],
                'user': serializer.data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Données JSON invalides'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erreur lors de la connexion utilisateur: {str(e)}")
        return Response({
            'error': 'Erreur lors de la connexion'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Vue pour rafraîchir un token JWT
    """
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Rafraîchir le token
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            return Response({
                'success': True,
                'access_token': access_token,
                'refresh_token': str(refresh),
                'token_type': 'Bearer',
                'expires_in': 86400
            }, status=status.HTTP_200_OK)
        except TokenError as e:
            logger.error(f"Erreur lors du refresh token: {str(e)}")
            return Response({
                'error': 'Token de rafraîchissement invalide'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Données JSON invalides'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erreur lors du refresh token: {str(e)}")
        return Response({
            'error': 'Erreur lors du rafraîchissement du token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Vue de déconnexion
    """
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Déconnecter en blacklistant le token
        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
            
            return Response({
                'success': True,
                'message': 'Déconnexion réussie'
            }, status=status.HTTP_200_OK)
        except TokenError as e:
            logger.error(f"Erreur lors de la déconnexion: {str(e)}")
            return Response({
                'error': 'Token invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Données JSON invalides'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {str(e)}")
        return Response({
            'error': 'Erreur lors de la déconnexion'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Vue pour récupérer le profil de l'utilisateur connecté
    """
    try:
        # Récupérer l'utilisateur depuis le token JWT
        user = get_user_from_token(request)
        
        if not user:
            return Response({
                'error': 'Token d\'authentification invalide'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Vérifier si c'est un admin
        if user.is_superuser or user.is_staff:
            user_type = 'superuser' if user.is_superuser else 'admin'
            response_data = {
                'user_type': user_type,
                'permissions': get_user_permissions(user),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_superuser': user.is_superuser,
                    'is_staff': user.is_staff,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login
                }
            }
        else:
            # C'est un utilisateur standard (professeur ou étudiant)
            user_roles = [role.name for role in user.roles.all()]
            
            if 'PROFESSOR' in user_roles:
                user_type = 'professor'
            elif 'STUDENT' in user_roles:
                user_type = 'student'
            else:
                user_type = 'user'
            
            serializer = UserSerializer(user)
            response_data = {
                'user_type': user_type,
                'roles': user_roles,
                'permissions': get_user_permissions(user),
                'user': serializer.data,
                'last_login': user.last_login,
                'account_status': {
                    'is_active': user.is_active
                }
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil: {str(e)}")
        return Response({
            'error': 'Erreur lors de la récupération du profil'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Vue pour changer le mot de passe
    """
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'error': 'Ancien et nouveau mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider la force du nouveau mot de passe
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer l'utilisateur depuis le token
        user = get_user_from_token(request)
        
        if not user:
            return Response({
                'error': 'Token d\'authentification invalide'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Vérifier l'ancien mot de passe
        if not user.check_password(current_password):
            return Response({
                'error': 'Ancien mot de passe incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Changer le mot de passe
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Mot de passe modifié avec succès'
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Données JSON invalides'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erreur lors du changement de mot de passe: {str(e)}")
        return Response({
            'error': 'Erreur lors du changement de mot de passe'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Endpoint pour demander la réinitialisation du mot de passe
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return Response({
                'error': "L'email est requis"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # Pour la sécurité, on ne révèle pas si l'email existe ou non
            return Response({
                'success': True, 
                'message': 'Si cet email existe, un lien de réinitialisation a été envoyé.'
            }, status=status.HTTP_200_OK)

        # Générer le token de réinitialisation (expire dans 5 minutes)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token_generator.make_token(user)
        
        # URL de réinitialisation (à adapter selon votre frontend)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}/"

        # Préparer l'email
        subject = "Réinitialisation de votre mot de passe - Gestion des Présences"
        context = {
            'user': user,
            'reset_url': reset_url,
        }
        
        # Utiliser le template HTML pour l'email
        html_message = render_to_string('reset_password_email.html', context)
        text_message = f"""Bonjour {user.first_name} {user.last_name},

Vous avez demandé la réinitialisation de votre mot de passe pour le système de gestion des présences.

Cliquez sur le lien ci-dessous pour le réinitialiser :
{reset_url}

Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.

Cordialement,
L'équipe de Gestion des Présences"""

        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return Response({
            'success': True, 
            'message': 'Si cet email existe, un lien de réinitialisation a été envoyé.'
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Données JSON invalides'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erreur lors de la demande de réinitialisation: {str(e)}")
        return Response({
            'error': 'Erreur lors de la demande de réinitialisation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Endpoint pour réinitialiser le mot de passe via le lien reçu par email
    """
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        uidb64 = data.get('uidb64')
        token = data.get('token')
        new_password = data.get('new_password')
        
        logger.info(f"Tentative de réinitialisation - uidb64: {uidb64}, token: {token}")
        
        if not (uidb64 and token and new_password):
            return Response({
                'error': 'uidb64, token et new_password sont requis',
                'details': f'Données reçues: {data}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider la force du nouveau mot de passe
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid, is_active=True)
            logger.info(f"Utilisateur trouvé: {user.email}")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
            return Response({
                'error': 'Lien invalide',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le token (expire dans 5 minutes)
        is_token_valid = password_reset_token_generator.check_token(user, token)
        logger.info(f"Vérification du token - valide: {is_token_valid}")
        
        if not is_token_valid:
            return Response({
                'error': 'Le lien de réinitialisation est invalide ou a expiré.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mettre à jour le mot de passe
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Mot de passe mis à jour pour l'utilisateur: {user.email}")
        
        return Response({
            'success': True, 
            'message': 'Mot de passe réinitialisé avec succès'
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON: {str(e)}")
        return Response({
            'error': 'Données JSON invalides',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation: {str(e)}", exc_info=True)
        return Response({
            'error': 'Erreur lors de la réinitialisation du mot de passe',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


