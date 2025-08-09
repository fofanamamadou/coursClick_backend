from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Absence
from .serializers import (
    AdminAbsenceSerializer,
    StudentAbsenceSerializer,
    StudentJustificationSerializer
)
from users.models import User
from planning.models import Planning
from pointage.models import Pointage, SessionPresence

class GenererAbsencesView(generics.GenericAPIView):
    """
    Vue API pour générer les absences pour une session de cours donnée.
    Accessible uniquement par un administrateur/professeur.
    Prend un `planning_id` en entrée.
    """
    permission_classes = [IsAdminUser] # À affiner, peut-être aussi pour les professeurs

    def post(self, request, *args, **kwargs):
        planning_id = request.data.get('planning_id')
        if not planning_id:
            return Response({"error": "planning_id est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            planning = Planning.objects.get(id=planning_id)
        except Planning.DoesNotExist:
            return Response({"error": "Planning non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        # Trouver la classe associée à ce planning (logique à adapter selon vos modèles)
        # Hypothèse : le module du planning est lié à une filière, qui a des classes
        # Cette partie est complexe et dépend de la structure exacte de vos modèles
        # Pour l'instant, on suppose que le prof du planning a une classe.
        # **CETTE LOGIQUE DEVRA ÊTRE ADAPTÉE PRÉCISÉMENT À VOTRE STRUCTURE**
        classe = planning.user.classe # Hypothèse simplifiée
        if not classe:
            return Response({"error": "Impossible de déterminer la classe pour ce planning."}, status=status.HTTP_400_BAD_REQUEST)

        etudiants_de_la_classe = User.objects.filter(classe=classe, roles__name='STUDENT')
        
        # Récupérer les sessions de présence actives pour ce planning
        sessions_presence = SessionPresence.objects.filter(planning=planning, is_active=True)
        if not sessions_presence.exists():
            return Response({"message": "Aucune session de présence active trouvée pour ce planning. Impossible de générer les absences."},
                            status=status.HTTP_404_NOT_FOUND)

        # Récupérer les IDs des étudiants qui ont pointé dans l'une de ces sessions
        etudiants_presents_ids = Pointage.objects.filter(session__in=sessions_presence).values_list('user_id', flat=True)

        # Trouver les étudiants absents
        etudiants_absents = etudiants_de_la_classe.exclude(id__in=etudiants_presents_ids)

        absences_creees = 0
        for etudiant in etudiants_absents:
            # Crée l'absence seulement si elle n'existe pas déjà
            _, created = Absence.objects.get_or_create(
                user=etudiant,
                planning=planning
            )
            if created:
                absences_creees += 1

        return Response({
            "message": f"{absences_creees} absence(s) créée(s) avec succès.",
            "total_etudiants_classe": etudiants_de_la_classe.count(),
            "etudiants_presents": len(etudiants_presents_ids),
            "etudiants_absents": etudiants_absents.count()
        }, status=status.HTTP_201_CREATED)


class StudentAbsenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les étudiants. 
    - `list`: voir ses propres absences.
    - `retrieve`: voir le détail d'une de ses absences.
    - `justifier`: soumettre un justificatif pour une absence.
    """
    serializer_class = StudentAbsenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Un étudiant ne peut voir que ses propres absences
        return Absence.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post', 'put'], serializer_class=StudentJustificationSerializer)
    def justifier(self, request, pk=None):
        absence = self.get_object()
        
        if absence.statut not in ['NON_JUSTIFIEE', 'EN_ATTENTE']:
            return Response({"error": "Cette absence ne peut plus être justifiée."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance=absence, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Retourner l'absence mise à jour avec le serializer d'étudiant complet
        return Response(StudentAbsenceSerializer(absence).data, status=status.HTTP_200_OK)


class AdminAbsenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les administrateurs.
    - CRUD complet sur les absences.
    - `approuver`: Marquer une absence comme approuvée.
    - `refuser`: Marquer une absence comme refusée.
    """
    queryset = Absence.objects.all()
    serializer_class = AdminAbsenceSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def approuver(self, request, pk=None):
        absence = self.get_object()
        absence.statut = 'APPROUVEE'
        absence.save()
        return Response(self.get_serializer(absence).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def refuser(self, request, pk=None):
        absence = self.get_object()
        absence.statut = 'REFUSEE'
        absence.save()
        return Response(self.get_serializer(absence).data, status=status.HTTP_200_OK)