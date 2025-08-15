from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsProfessor, IsAnyAdmin
from .serializers import PlanningSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Planning
from module.models import Module
from datetime import datetime, timedelta, date
from absences.utils import generer_absences_pour_planning
from django.utils import timezone
from users.models import User
from django.db.models import Q
from datetime import datetime, date


# Create your views here.

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def planning_view(request):
    if request.method == 'POST':
        # Vérifie si on reçoit une liste de plannings ou un seul
        is_many = isinstance(request.data, list)
        serializer = PlanningSerializer(data=request.data, many=is_many)

        #Pour eviter les doublons
        if is_many:
            for item in request.data:
                user_id = item["user"]
                horaire_id = item["horaire"]
                date = item["date"]

                # On récupère les conflits existants
                conflits = Planning.objects.filter(
                    user_id=user_id,
                    horaire_id=horaire_id,
                    date=date
                )

                if conflits.exists():
                    dates_conflit = [p.date.strftime("%d-%m-%Y") for p in conflits]
                    return Response(
                        {
                            "error": f"Conflit : Ce professeur a déjà un planning pour ces dates et horaires.",
                            "dates_conflit": dates_conflit
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        planning_list = Planning.objects.all()
        serializer = PlanningSerializer(planning_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
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

    if planning.is_validated_by_professor:
        return Response({"message": "Votre présence a déjà été validé pour cet cours."}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({"message": "Vous ne pouvez valider votre présence qu’après la fin du cours."}, status=status.HTTP_400_BAD_REQUEST)

    if now > datetime_fin + timedelta(hours=1):
        return Response({"message": "Le délai de validation de la présence est dépassé (1h après la fin du cours)."}, status=status.HTTP_400_BAD_REQUEST)

    # Validation réussie
    planning.is_validated_by_professor = True
    planning.save()

    # On déclenche la génération des absences
    resultat = generer_absences_pour_planning(planning)
    
    message_final = f"Vore présence a été validé avec succès. {resultat.get('absences_creees', 0)} absence(s) enregistrée(s) pour cet cours."

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
@permission_classes([IsAuthenticated, IsAnyAdmin])
def validateCoursByAdmin(request, id):
    """
    Vue admin pour valider manuellement un cours par un admin
    """
    planning = Planning.objects.filter(pk=id).first()

    if not planning:
        return Response({"message": f"Planning non trouvé avec ID: {id}"}, status=status.HTTP_404_NOT_FOUND)

    if planning.is_is_validated_by_admind_by_admin:
        return Response({"message": "Cette présence est déjà validé par un administrateur."}, status=status.HTTP_400_BAD_REQUEST)

    planning.is_is_validated_by_admind_by_admin = True
    planning.save()

    return Response({"message": "La présence a été validé avec succès par un administrateur."}, status=status.HTTP_200_OK)


# Vue pour récupérer les plannings par date
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_plannings_by_date(request):
    """
    Récupère tous les plannings pour une date donnée.
    Paramètre: ?date=YYYY-MM-DD
    """
    date_param = request.query_params.get('date')
    if not date_param:
        return Response({'error': 'Le paramètre "date" est requis (format: YYYY-MM-DD)'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                        status=status.HTTP_400_BAD_REQUEST)

    plannings = Planning.objects.filter(date=target_date)
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vue pour récupérer les plannings par utilisateur
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_plannings_by_user(request, user_id):
    """
    Récupère tous les plannings d'un utilisateur spécifique.
    """
    try:
        
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': f'Utilisateur non trouvé avec ID: {user_id}'},
                        status=status.HTTP_404_NOT_FOUND)

    plannings = Planning.objects.filter(user=user)
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vue pour récupérer les plannings par module
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_plannings_by_module(request, module_id):
    """
    Récupère tous les plannings d'un module spécifique.
    """
    try:
        module = Module.objects.get(pk=module_id)
    except Module.DoesNotExist:
        return Response({'error': f'Module non trouvé avec ID: {module_id}'},
                        status=status.HTTP_404_NOT_FOUND)

    plannings = Planning.objects.filter(module=module)
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vue pour récupérer les plannings validés par les professeurs
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_validated_plannings_by_professor(request):
    """
    Récupère tous les plannings validés (is_validated_by_professor=True).
    """
    plannings = Planning.objects.filter(is_validated_by_professor=True)
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vue pour récupérer les plannings en attente de validation d'un admin
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_pending_plannings(request):
    """
    Récupère tous les plannings en attente de validation.
    """
    plannings = Planning.objects.filter(is_validated_by_professor=True, is_validated_by_admin=False)
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vue pour récupérer les statistiques des plannings
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_planning_stats(request):
    """
    Récupère les statistiques des plannings.
    """
    total_plannings = Planning.objects.count()
    is_validated_by_admind_by_prof = Planning.objects.filter(is_validated_by_professor=True).count()
    is_validated_by_admind_by_admin = Planning.objects.filter(is_validated_by_admin=True).count()
    pending_plannings = Planning.objects.filter(is_validated_by_professor=False, is_validated_by_admin=False).count()

    # Statistiques par utilisateur connecté (si c'est un professeur)
    user_stats = {}
    if hasattr(request.user, 'modules') and request.user.modules.exists():
        user_plannings = Planning.objects.filter(user=request.user)
        user_stats = {
            'mes_plannings_total': user_plannings.count(),
            'mes_plannings_valides': user_plannings.filter(is_validated_by_professor=True).count(),
            'mes_plannings_en_attente': user_plannings.filter(is_validated_by_professor=False, is_validated_by_admin=False).count(),
        }

    stats = {
        'total': total_plannings,
        'is_validated_by_professor': is_validated_by_admind_by_prof,
        'is_validated_by_admind_by_admin': is_validated_by_admind_by_admin,
        'pending': pending_plannings,
        'completion_rate': round((is_validated_by_admind_by_prof / total_plannings * 100), 2) if total_plannings > 0 else 0,
        'user_stats': user_stats
    }

    return Response(stats, status=status.HTTP_200_OK)


# Vue pour récupérer les plannings par période
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_plannings_by_date_range(request):
    """
    Récupère les plannings entre deux dates.
    Paramètres: ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    start_date_param = request.query_params.get('start_date')
    end_date_param = request.query_params.get('end_date')

    if not start_date_param or not end_date_param:
        return Response({
            'error': 'Les paramètres "start_date" et "end_date" sont requis (format: YYYY-MM-DD)'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
    except ValueError:
        return Response({
            'error': 'Format de date invalide. Utilisez YYYY-MM-DD'
        }, status=status.HTTP_400_BAD_REQUEST)

    if start_date > end_date:
        return Response({
            'error': 'La date de début doit être antérieure à la date de fin'
        }, status=status.HTTP_400_BAD_REQUEST)

    plannings = Planning.objects.filter(date__range=[start_date, end_date])
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vue pour récupérer les plannings du jour en cours
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_today_plannings(request):
    """
    Récupère tous les plannings d'aujourd'hui.
    """
    today = date.today()
    plannings = Planning.objects.filter(date=today)
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vue pour récupérer les plannings de cette semaine
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def get_week_plannings(request):
    """
    Récupère tous les plannings de la semaine en cours.
    """
    today = date.today()
    # Calculer le début de la semaine (lundi)
    start_week = today - timedelta(days=today.weekday())
    # Calculer la fin de la semaine (dimanche)
    end_week = start_week + timedelta(days=6)

    plannings = Planning.objects.filter(date__range=[start_week, end_week])
    serializer = PlanningSerializer(plannings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Vue pour marquer un planning comme non validé (reset)
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAnyAdmin])
def reset_planning_validation(request, id):
    """
    Remet à zéro la validation d'un planning (admin uniquement).
    """
    planning = Planning.objects.filter(pk=id).first()

    if not planning:
        return Response({
            'message': f'Planning non trouvé avec ID: {id}'
        }, status=status.HTTP_404_NOT_FOUND)

    planning.is_validated_by_professor = False
    planning.is_validated_by_admin = False
    planning.save()

    return Response({
        'message': 'La validation du planning a été réinitialisée avec succès.'
    }, status=status.HTTP_200_OK)


# Vue pour obtenir les plannings d'un professeur par semaine
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsProfessor])
def get_professor_week_schedule(request):
    """
    Récupère le planning de la semaine pour le professeur connecté,
    organisé par jour.
    """

    today = date.today()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)

    plannings = Planning.objects.filter(
        user=request.user,
        date__range=[start_week, end_week]
    ).order_by('date', 'horaire__time_start_course')

    # Organiser par jour
    schedule_by_day = {}
    current_date = start_week

    # Initialiser tous les jours de la semaine
    days_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    for i in range(7):
        day_date = start_week + timedelta(days=i)
        schedule_by_day[days_names[i]] = {
            'date': day_date.strftime('%Y-%m-%d'),
            'plannings': []
        }

    # Remplir avec les plannings existants
    for planning in plannings:
        day_name = days_names[planning.date.weekday()]
        schedule_by_day[day_name]['plannings'].append(
            PlanningSerializer(planning).data
        )

    return Response(schedule_by_day, status=status.HTTP_200_OK)