from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes

from .models import Role
from users.models import User
from rest_framework import status
from rest_framework.response import Response
from .serializers import RoleSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# Create your views here.

@api_view(['POST','GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def role_view(request) :
    """
        API de création ou d'ajout des profils dans la table AppRole et récupération de la liste des profils.
        """
    if request.method == 'POST' :
        # Récuperons des données du formulaire
        serializer = RoleSerializer(data = request.data)
        #Verifier si les donnees sont valide
        if serializer.is_valid() :
            serializer.save()
            return Response(serializer.data, status= status.HTTP_201_CREATED )
        print(serializer.errors)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET' :
        # Récuperation de toutes les role dans la table Role
        role_list = Role.objects.all()
        serializer = RoleSerializer(role_list, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def set_role_to_user_view(request, user_pk, role_pk):
#     """
#     API d'affectation d'un profil (AppRole) à un utilisateur (User).
#     """
#
#     # Récupérer l'utilisateur dans la table User pour pouvoir l'attribuer un profil
#     user = User.objects.filter(pk = user_pk).first()
#     if not user:
#         return Response(data= {'message': f'Utilisateur non trouvé avec ID:{user_pk} '}, status= status.HTTP_404_NOT_FOUND)
#
#     # Récupéré dans la table AppRole le profil qu'on souhaite donner à l'utilisateur
#     role = Role.objects.filter(pk = role_pk).first()
#     if not role:
#         return Response(data= {'message': f'Role non trouvé avec ID:{role_pk} '}, status= status.HTTP_404_NOT_FOUND)
#
#     user.roles.add(role)
#     user.save()
#     return Response(data= {'message': 'Profil affecté avec succès !'}, status= status.HTTP_200_OK)

