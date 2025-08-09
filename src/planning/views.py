from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsProfessor
from .serializers import PlanningSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Planning
from datetime import datetime, timedelta, date
from absences.utils import generer_absences_pour_planning
from django.utils import timezone

# Create your views here.

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def planning_view(request):
    if request.method == 'POST':
        # Vérifie si on reçoit une liste de plannings ou un seul
        is_many = isinstance(request.data, list)
        serializer = PlanningSerializer(data=request.data, many=is_many)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        planning_list = Planning.objects.all()
        serializer = PlanningSerializer(planning_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def planning_detail_view(request, id):
    planning = Planning.objects.filter(pk=id).first()

    if not planning:
        return Response({"message": f"Planning non trouvé avec ID : {id}"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PlanningSerializer(planning)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = PlanningSerializer(planning, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        planning.delete()
        return Response({"message": "Planning supprimé"}, status=status.HTTP_204_NO_CONTENT)



@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsProfessor])
def valider_cours(request, id):
    """
    API pour valider un cours, uniquement le jour même et dans un délai de 1h après la fin du cours.
    """
    planning = Planning.objects.filter(pk=id).select_related('horaire').first()
    if not planning:
        return Response({"message": f"Cours non trouvé avec ID: {id}"}, status=status.HTTP_404_NOT_FOUND)

    if planning.his_state:
        return Response({"message": "Ce cours a déjà été validé."}, status=status.HTTP_400_BAD_REQUEST)

    now = timezone.localtime()
    today = date.today()

    if planning.date != today:
        return Response({"message": "La validation est uniquement possible le jour même du cours."}, status=status.HTTP_400_BAD_REQUEST)

    horaire = planning.horaire
    if not horaire:
        return Response({"message": "Aucune information d'horaire associée à ce cours."}, status=status.HTTP_400_BAD_REQUEST)

    # Fusionner la date du cours avec l’heure de fin de l’horaire
    datetime_fin = datetime.combine(planning.date, horaire.time_end_course)
    datetime_fin = timezone.make_aware(datetime_fin)

    if now < datetime_fin:
        return Response({"message": "Vous ne pouvez valider un cours qu’après sa fin."}, status=status.HTTP_400_BAD_REQUEST)

    if now > datetime_fin + timedelta(hours=1):
        return Response({"message": "Le délai de validation du cours est dépassé (1h après la fin)."}, status=status.HTTP_400_BAD_REQUEST)

    # Validation réussie
    planning.his_state = True
    planning.save()

    # On déclenche la génération des absences
    resultat = generer_absences_pour_planning(planning)
    
    message_final = f"Cours validé avec succès. {resultat.get('absences_creees', 0)} absence(s) enregistrée(s)."

    return Response({"message": message_final}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsProfessor])
def get_user_plannings(request):
    """
    Retourne la liste des plannings de l'utilisateur connecté pour aujourd'hui.
    """
    user = request.user
    today = date.today()
    plannings = Planning.objects.filter(user=user, date=today)
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def validateCoursByAdmin(request, id):
    """
    Vue admin pour valider manuellement un cours en mettant `validate = True`.
    """
    planning = Planning.objects.filter(pk=id).first()

    if not planning:
        return Response({"message": f"Planning non trouvé avec ID: {id}"}, status=status.HTTP_404_NOT_FOUND)

    if planning.validate:
        return Response({"message": "Ce cours est déjà marqué comme validé."}, status=status.HTTP_400_BAD_REQUEST)

    planning.validate = True
    planning.save()

    return Response({"message": "Le cours a été validé avec succès par un administrateur."}, status=status.HTTP_200_OK)