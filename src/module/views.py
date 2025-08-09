from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import ModuleSerializers
from rest_framework.permissions import IsAuthenticated
from .models import Module
# Create your views here.

@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def module_view  (request):
    if request.method =='POST' :
        serializer = ModuleSerializers(data=request.data)
        if serializer.is_valid() :
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status =status.HTTP_400_BAD_REQUEST)
    elif request.method =='GET' :
        module_list = Module.objects.all()
        serializer = ModuleSerializers(module_list, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)


@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def module_detail_view(request, id) :
    module = Module.objects.filter(pk=id).first()

    if not module:
        return Response(data={"message": f"Module non trouve avec ID :{id} "}, status= status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ModuleSerializers(module)
        return Response(serializer.data, status= status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = ModuleSerializers(module, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        module.delete()
        return Response({"message": "Module supprimée"}, status=status.HTTP_204_NO_CONTENT)