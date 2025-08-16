import os
import datetime
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsSuperuser, IsAnyAdmin
from .models import User
from users.serializers import UserSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .utils import send_mail_html

from django.utils.crypto import get_random_string


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def users_view(request):
    """
    API de création ou d'ajout d'un nouvel utilisateur et Récupération de la liste des utilisateurs.
    """
    if request.method == 'POST':
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            email = request.data['email']
            first_name = request.data['first_name']

            user = User.objects.filter(email=email).first()
            password = get_random_string(8)
            user.set_password(password)
            user.save()

            subject = "Account | FaceLoadIdentity"
            custom_template = 'email.html'
            context = {
                "date": datetime.date.today(),
                "email": email,
                "password": password,
                "first_name": first_name
            }
            receivers = [email]
            send_mail_html(subject=subject,  receivers=receivers, template=custom_template, context=context)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        users = User.get_noadmins()
        serializer = UserSerializer(users, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)


@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def users_details_view(request, id) :
    user = User.objects.filter(pk=id).first()

    if not user:
        return Response(data={"message": f"Utilisateur non trouve avec ID :{id} "}, status= status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data, status= status.HTTP_200_OK)

    if not request.user.is_superuser:
        return Response({"message": "Action non autorisée."}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response({"message": "Utilisateur supprimée"}, status=status.HTTP_204_NO_CONTENT)


#Recuperer la liste des etudiants
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def list_students(request):
    students = User.get_students()
    serializer = UserSerializer(students, many=True)
    return Response(serializer.data)

#Recuperer la liste des professeurs
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def list_professors(request):
    professors = User.get_professors()
    serializer = UserSerializer(professors, many=True)
    return Response(serializer.data)

#Recuperer la liste des admins
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperuser])
def list_admins(request):
    admins = User.get_regular_admins()
    serializer = UserSerializer(admins, many=True)
    return Response(serializer.data)



@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsSuperuser])
def disable_user_view(request, user_pk):
    """
    API pour desactiver ou activer un Utilisateur
    """
    if request.method == "PUT":
        user = User.objects.filter(pk = user_pk).first()
        if not user:
            return Response(data= {"message": f"Utilisateur non trouvé avec ID:{user_pk} "}, status=status.HTTP_404_NOT_FOUND)
        user.is_active = not user.is_active
        user.save()
        action = "désactivé" if not user.is_active else "activé"
        return Response({"message": f"Utilisateur {action} avec succès."}, status=status.HTTP_200_OK)


#Fonction pour creer des admins
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperuser])
def create_admin_view(request):
    email = request.data.get('email')
    password = get_random_string(8)
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')


    if not email or not password:
        return Response({"message": "L'e-mail et le mot de passe sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"message": "Un utilisateur avec cet e-mail existe déjà."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(email=email, password=password, first_name = first_name, last_name =last_name, is_staff=True, is_superuser=False)

    subject = "Password | CoursClick"
    custom_template = 'new_password.html'
    context = {
        "date": datetime.date.today(),
        "email": email,
        "new_password": password,
        "first_name": first_name
    }
    receivers = [email]
    send_mail_html(subject=subject, receivers=receivers, template=custom_template, context=context)

    return Response({"message": f"Administrateur créé : {user.email}"}, status=status.HTTP_201_CREATED)
