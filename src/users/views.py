import os
import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsProfessor, IsStudent, IsSuperuser, IsAnyAdmin, IsRegularAdmin
from rest_framework.response import Response
from rest_framework import  status
from .models import User
from .models import Role
from .serializers import UserSerializer
from .serializers import RoleSerializer
from .utils import send_mail_html
from module.serializers import ModuleSerializers

from django.utils.crypto import get_random_string

# Constante pour régler la tolérance de correspondance
FACE_MATCH_THRESHOLD = 0.65





@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def users_view(request):
    """
    API de création ou d'ajout d'un nouvel utilisateur et Récupération de la liste des utilisateurs.
    """
    if request.method == 'POST':
        # Récupérer les données du formulaire pour les transformer en Model.
        serializer = UserSerializer(data = request.data)
        # Vérifier si les données du formulaire sont valides, on enregistre les données
        if serializer.is_valid():
            serializer.save()
            #Recuperer certains infos du formulaires, pour l'envoie du mail et d'autres operations
            email = request.data['email']
            first_name = request.data['first_name']


            # Récupérer l'utilisateur dans la base de donnée avec l'email
            user = User.objects.filter(email=email).first()
            # Renommer la photo
            if user.photo:
                original_path = user.photo.path
                extension = os.path.splitext(original_path)[1]  # ex: '.jpg'
                new_filename = f"user_{user.id}{extension}"
                new_path = os.path.join(os.path.dirname(original_path), new_filename)

                os.rename(original_path, new_path)

                # Mettre à jour le nom stocké dans la base
                user.photo.name = f"photos/{new_filename}"
                user.save(update_fields=['photo'])
            # Générer un mot de passe pour l'utilisateur
            password = get_random_string(8)
            #L'attribuer a l'utilisatur
            user.set_password(password)
            user.save()

            # Le sujet ou l'objet du mail
            subject = "Account | FaceLoadIdentity"
            # Le template html qu'on souhaite envoyer
            custom_template = 'email.html'
            # Les variables qu'on souhaite transmèttre le mail
            context = {
                "date": datetime.date.today(),
                "email": email,
                "password": password,
                "first_name": first_name
            }
            receivers = [email]
            # Appeler notre fonction pour envoyer le mail
            send_mail_html(subject=subject,  receivers=receivers, template=custom_template, context=context)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        # Récupérer les utilisateurs non admins dans la table user
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
    
    # Seuls les superutilisateurs peuvent modifier ou supprimer
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

@api_view(['POST'])
def reset_password_view(request):
    # Récuperer l'email de l'utilisateur dans le formulaire
    email = request.data['email']

    # Récupérer l'utilisateur dans la base de donnée ayant ce mail
    user = User.objects.filter(email= email).first()

    if not user:
        return Response(data= {"message": "E-mail incorrect !"}, status= status.HTTP_404_NOT_FOUND)

    # Générer un nouveau mot de passe pour l'utilisateur
    new_password = get_random_string(8)

    user.set_password(new_password)
    user.save()

    # Envoyer le nouveau mot de passe par mail
    subject = "New password | FaceLoadIdentity"
    # Le template html qu'on souhaite envoyer
    custom_template = 'new_password.html'
    first_name = user.first_name
    # Les variables qu'on souhaite transmèttre le mail
    context = {
        "date": datetime.date.today(),
        "email": email,
        "new_password": new_password,
        "first_name": first_name
    }
    receivers = [email]
    # Appeler notre fonction pour envoyer le mail
    send_mail_html(subject=subject, receivers=receivers, template=custom_template, context=context)
    return Response(data= {"message": "Vérifier votre boîte mail !"}, status= status.HTTP_200_OK)




#@api_view(['GET'])
#@permission_classes([IsAuthenticated])
#def user_detail_view(request, user_pk):
 #   """
  #  API pour retrouver un utilisateur par son ID
   # """
    #user = User.objects.filter(pk = user_pk).first()

    # Vérifier si l'utilisateur existe
    #if not user:
    #    return Response(data={"message": f"Utilisateur non trouvé avec ID:{user_pk} "}, status= status.HTTP_404_NOT_FOUND)

   # if request.method == "GET":
    #    serializer = UserSerializer(user)
  #      return Response(serializer.data, status= status.HTTP_200_OK)


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

#Recuperer la liste des personnels
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def list_personnels(request):
    personnels = User.get_personnels()
    serializer = UserSerializer(personnels, many=True)
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
        user.is_active = not user.is_active  # Inverse l'état actuel
        user.save()
        action = "désactivé" if not user.is_active else "activé"
        return Response({"message": f"Utilisateur {action} avec succès."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password_view(request):
    # Récupérer l'utilisateur connecté
    user = request.user

    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    password_confirm = request.data.get('password_confirm')

    # Vérifier si l'ancien mot de passe de l'utilisateur est correcte
    if not user.check_password(old_password):
        return Response(data= {"message": "Ancien mot de passe incorrect !"}, status= status.HTTP_400_BAD_REQUEST)

    if new_password != password_confirm:
        return Response(data= {"message": "Nouveau mot de passe et le mot de passe de confirmation sont incorrecte !"}, status= status.HTTP_400_BAD_REQUEST)

    # Mises à jour du mot de passe
    user.set_password(new_password)
    user.save()
    return Response(data= {"message": "Mot de passe changé avec succès !"}, status= status.HTTP_200_OK)



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

    # Créer un admin (is_staff=True, is_superuser=False)
    user = User.objects.create_user(email=email, password=password, first_name = first_name, last_name =last_name, is_staff=True, is_superuser=False)

    # Envoyer le mot de passe par mail
    subject = "Password | FaceLoadIdentity"
    # Le template html qu'on souhaite envoyer
    custom_template = 'new_password.html'
    # Les variables qu'on souhaite transmèttre le mail
    context = {
        "date": datetime.date.today(),
        "email": email,
        "new_password": password,
        "first_name": first_name
    }
    receivers = [email]
    # Appeler notre fonction pour envoyer le mail
    send_mail_html(subject=subject, receivers=receivers, template=custom_template, context=context)

    return Response({"message": f"Administrateur créé : {user.email}"}, status=status.HTTP_201_CREATED)


from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Fonction pour recuperer les modules d'un professeur
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_professor_modules(request, professor_id):
    """
    API pour récupérer les modules d'un professeur via son ID
    """
    user = User.objects.filter(id=professor_id, roles__name='PROFESSOR').first()

    if not user:
        return Response({"message": f"Aucun professeur trouvé avec l'ID : {professor_id}"}, status=status.HTTP_404_NOT_FOUND)

    modules = user.modules.all()
    serializer = ModuleSerializers(modules, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
