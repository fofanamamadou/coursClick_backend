
from django.http import JsonResponse
from django.db.models import Count
from datetime import date, timedelta

# Importation des modèles
from users.models import User
from planning.models import Planning
from absences.models import Absence
from pointage.models import Pointage

def dashboard_api_view(request):
    """
    Vue d'API qui retourne toutes les données nécessaires pour le dashboard admin.
    Inclut les KPIs et les données pour les graphiques d'absences.
    """
    today = date.today()
    one_week_ago = today - timedelta(days=7)

    # --- Section KPIs ---

    # Taux de présence
    total_students = User.get_students().filter(is_active=True).count()
    students_present_today = Pointage.objects.filter(timestamp__date=today).values('user').distinct().count()
    attendance_rate = (students_present_today / total_students) * 100 if total_students > 0 else 0

    # Plannings du jour
    plannings_today = Planning.objects.filter(date=today)
    total_plannings_today = plannings_today.count()
    validated_plannings = plannings_today.filter(is_validated_by_admin=True).count()
    cancelled_plannings = plannings_today.filter(is_validated_by_professor=True, is_validated_by_admin=False).count()
    scheduled_plannings = total_plannings_today - validated_plannings - cancelled_plannings

    # Utilisateurs actifs
    active_students = total_students
    active_professors = User.get_professors().filter(is_active=True).count()

    # Absences non justifiées
    unjustified_absences_week = Absence.objects.filter(
        cree_le__date__gte=one_week_ago,
        statut='NON_JUSTIFIEE'
    ).count()

    # --- Section Données pour Graphiques ---

    absences = Absence.objects.filter(statut='NON_JUSTIFIEE')

    # Données par Filière
    filiere_data = absences.values('planning__horaire__module__filieres__name').annotate(count=Count('id')).order_by('-count')
    filiere_labels = [item['planning__horaire__module__filieres__name'] for item in filiere_data if item['planning__horaire__module__filieres__name']]
    filiere_counts = [item['count'] for item in filiere_data if item['planning__horaire__module__filieres__name']]

    # Données par Module
    module_data = absences.values('planning__horaire__module__name').annotate(count=Count('id')).order_by('-count')
    module_labels = [item['planning__horaire__module__name'] for item in module_data if item['planning__horaire__module__name']]
    module_counts = [item['count'] for item in module_data if item['planning__horaire__module__name']]

    # Données par Classe
    classe_data = absences.values('planning__horaire__module__classe__name').annotate(count=Count('id')).order_by('-count')
    classe_labels = [item['planning__horaire__module__classe__name'] for item in classe_data if item['planning__horaire__module__classe__name']]
    classe_counts = [item['count'] for item in classe_data if item['planning__horaire__module__classe__name']]

    # --- Construction de la réponse JSON ---

    response_data = {
        'kpis': {
            'attendance_rate': round(attendance_rate, 2),
            'plannings_today': {
                'total': total_plannings_today,
                'validated': validated_plannings,
                'cancelled': cancelled_plannings,
                'scheduled': scheduled_plannings,
            },
            'active_users': {
                'students': active_students,
                'professors': active_professors,
            },
            'unjustified_absences_week': unjustified_absences_week,
        },
        'charts': {
            'absences_by_filiere': {
                'labels': filiere_labels,
                'data': filiere_counts,
            },
            'absences_by_module': {
                'labels': module_labels,
                'data': module_counts,
            },
            'absences_by_classe': {
                'labels': classe_labels,
                'data': classe_counts,
            },
        }
    }

    return JsonResponse(response_data)
