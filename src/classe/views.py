from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from .models import Classe
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ClasseSerializers


# Create your views here.
@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def classe_view(request):
    if request.method=='POST':
        serializer =ClasseSerializers(data = request.data)
        if serializer.is_valid() :
            serializer.save()
            return Response(serializer.data, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET':
        classe_list = Classe.objects.all()
        serializer = ClasseSerializers(classe_list, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)

@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def classe_detail_view(request, id) :
    classe = Classe.objects.filter(pk=id).first()

    if not classe:
        return Response(data={"message": f"Classe non trouve avec ID :{id} "}, status= status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ClasseSerializers(classe)
        return Response(serializer.data, status= status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = ClasseSerializers(classe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        classe.delete()
        return Response({"message": "Classe supprimée"}, status=status.HTTP_204_NO_CONTENT)
