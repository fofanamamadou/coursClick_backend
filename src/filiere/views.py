from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes

from .models import Filiere
from rest_framework import status
from rest_framework.response import Response
from .serializers import FiliereSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.

@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def filiere_view(request) :
    if request.method == 'POST' :
        # Récuperons des données du formulaire
        serializer = FiliereSerializer(data = request.data)
        #Verifier si les donnees sont valide
        if serializer.is_valid() :
            serializer.save()
            return Response(serializer.data, status= status.HTTP_201_CREATED )
        print(serializer.errors)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET' :
        # Récuperation de toutes les filieres dans la table Filiere
        filiere_list = Filiere.objects.all()
        serializer = FiliereSerializer(filiere_list, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)

@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def filiere_detail_view(request, id) :
    filiere = Filiere.objects.filter(pk=id).first()

    if not filiere:
        return Response(data={"message": f"Filiere non trouve avec ID :{id} "}, status= status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        # Utilisez l'instance "filiere" que vous avez récupérée
        serializer = FiliereSerializer(filiere)
        return Response(serializer.data, status= status.HTTP_200_OK)
    elif request.method == 'PUT':
        # Mettez à jour l'instance "filiere" avec les nouvelles données
        serializer = FiliereSerializer(filiere, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        filiere.delete()
        return Response({"message": "filiere supprimée"}, status=status.HTTP_204_NO_CONTENT)