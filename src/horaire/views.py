from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from  rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Horaire
from users.permissions import IsProfessor, IsStudent
from module.models import Module


from .serializers import HoraireSerializer
from module.serializers import ModuleSerializers


# Create your views here.
@api_view(['POST','GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def horaire_view(request) :
    if request.method=='POST' :
        serializer = HoraireSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED )
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET' :
        horaire_list = Horaire.objects.all()
        serializer = HoraireSerializer(horaire_list, many=True)
        return Response(serializer.data, status= status.HTTP_200_OK)

@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def horaire_detail_view(request, id) :
    horaire = Horaire.objects.filter(pk=id).first()

    if not horaire:
        return Response(data={"message": f"Absence non trouve avec ID :{id} "}, status= status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = HoraireSerializer(horaire)
        return Response(serializer.data, status= status.HTTP_200_OK)
    elif request.method == 'PUT':
        serializer = HoraireSerializer(horaire, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        horaire.delete()
        return Response({"message": "Absence supprimée"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def horaires_par_module(request, module_id):
    """
    API pour retourner la liste des horaires d’un module spécifique.
    """
    try:
        module = Module.objects.get(pk=module_id)
    except Module.DoesNotExist:
        return Response({"message": f"Module non trouvé avec ID: {module_id}"}, status=status.HTTP_404_NOT_FOUND)

    horaires = Horaire.objects.filter(module=module)
    serializer = HoraireSerializer(horaires, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsProfessor ])
def horaires_professeur_view(request):
    """
    Récupère tous les horaires d’un professeur connecté à un jour donné (ex: ?jour=Lundi).
    """
    jour = request.query_params.get('jour')
    if not jour:
        return Response({'error': 'Le paramètre "jour" est requis.'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user

    horaires = Horaire.objects.filter(jours__iexact=jour, module__in=user.modules.all())
    serializer = HoraireSerializer(horaires, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudent])
def horaires_etudiant_view(request):
    """
    Récupère tous les horaires d’un étudiant connecté à un jour donné (ex: ?jour=Lundi).
    """
    jour = request.query_params.get('jour')
    if not jour:
        return Response({'error': 'Le paramètre "jour" est requis.'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user

    # Récupère tous les modules de la classe
    horaires = Horaire.objects.filter(jours__iexact=jour, module__in=user.modules.all())
    serializer = HoraireSerializer(horaires, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
