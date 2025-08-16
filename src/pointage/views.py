from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string
from geopy.distance import geodesic

from .models import SessionPresence, Pointage, Planning
from .serializers import CreateSessionPresenceSerializer, ValidatePresenceSerializer, SessionPresenceSerializer, PointageSerializer, StudentPresenceSerializer
from users.models import User
from users.permissions import IsProfessor, IsStudent

def generate_unique_code():
    """Génère un code alphanumérique unique de 6 caractères."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not SessionPresence.objects.filter(code=code, is_active=True).exists():
            return code

class CreateSessionPresenceView(APIView):
    """
    Vue pour qu'un professeur puisse créer une session de présence.
    """
    permission_classes = [IsProfessor]

    def post(self, request, *args, **kwargs):
        serializer = CreateSessionPresenceSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            planning_id = validated_data['planning_id']

            try:
                planning = Planning.objects.get(id=planning_id)
            except Planning.DoesNotExist:
                return Response({'error': 'Planning non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

            if planning.user != request.user:
                 return Response({'error': 'Vous n\'etes pas autorise a lancer l\'appel pour ce cours.'}, status=status.HTTP_403_FORBIDDEN)

            now = timezone.now()
            course_start_time = timezone.make_aware(datetime.combine(planning.date, planning.horaire.time_start_course))
            course_end_time = timezone.make_aware(datetime.combine(planning.date, planning.horaire.time_end_course))
            generation_deadline = course_end_time - timedelta(minutes=30)

            if not (course_start_time <= now <= generation_deadline):
                return Response({
                    'error': 'La génération du code de présence n\'est possible qu\'entre le début du cours et 30 minutes avant la fin.'
                }, status=status.HTTP_403_FORBIDDEN)

            session = SessionPresence.objects.create(
                planning=planning,
                code=generate_unique_code(),
                latitude=validated_data['latitude'],
                longitude=validated_data['longitude'],
                end_time=timezone.now() + timedelta(minutes=5)
            )

            response_serializer = SessionPresenceSerializer(session)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidatePresenceView(APIView):
    """
    Vue pour qu'un étudiant puisse valider sa présence.
    """
    permission_classes = [IsStudent]

    def post(self, request, *args, **kwargs):
        serializer = ValidatePresenceSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            code = validated_data['code']
            student_coords = (validated_data['latitude'], validated_data['longitude'])

            try:
                session = SessionPresence.objects.get(code=code, is_active=True, end_time__gte=timezone.now())
            except SessionPresence.DoesNotExist:
                return Response({'error': 'Code de session invalide ou expiré.'}, status=status.HTTP_404_NOT_FOUND)

            professor_coords = (session.latitude, session.longitude)
            distance = geodesic(student_coords, professor_coords).meters

            if distance > 100:
                return Response({
                    'error': 'Vous êtes trop loin de la salle de classe.',
                    'distance_meters': round(distance)
                }, status=status.HTTP_403_FORBIDDEN)

            # Vérifier si l'étudiant est inscrit au cours
            planning = session.planning
            module_du_cours = planning.module
            if not module_du_cours or not module_du_cours.classe:
                return Response({'error': 'Impossible de vérifier la classe pour ce cours.'}, status=status.HTTP_400_BAD_REQUEST)

            if request.user.classe != module_du_cours.classe:
                 return Response({'error': 'Vous n\'etes pas inscrit a ce cours.'}, status=status.HTTP_403_FORBIDDEN)

            pointage, created = Pointage.objects.get_or_create(
                session=session,
                user=request.user
            )

            if not created:
                return Response({'message': 'Votre presence a deja ete enregistree.'}, status=status.HTTP_200_OK)

            return Response({'message': 'Presence validee avec succes !'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PointageListView(generics.ListAPIView):
    """
    Vue pour lister toutes les présences des étudiants, avec pagination.
    Accessible uniquement par les administrateurs.
    """
    serializer_class = PointageSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Pointage.objects.select_related('user', 'session__planning').all().order_by('-timestamp')

@api_view(['GET'])
@permission_classes([IsProfessor])
def list_presences_today_view(request):
    """
    Vue pour lister les présences du cours actuellement en session
    pour le professeur connecté.
    """
    now = timezone.now()
    today = now.date()
    current_time = now.time()

    try:
        session = SessionPresence.objects.get(
            planning__user=request.user,
            planning__date=today,
            planning__horaire__time_start_course__lte=current_time,
            planning__horaire__time_end_course__gte=current_time,
            is_active=True
        )
    except SessionPresence.DoesNotExist:
        return Response([], status=status.HTTP_200_OK)

    expected_students = User.objects.filter(
        classe=session.planning.module.classe,
        roles__name='STUDENT'
    ).distinct()

    present_students_ids = Pointage.objects.filter(session=session).values_list('user_id', flat=True)

    student_list = []
    for student in expected_students:
        presence_status = "Présent" if student.id in present_students_ids else "Absent"
        student_list.append({
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'classe': student.classe.name if student.classe else None,
            'filiere': student.filiere.name if student.filiere else None,
            'status': presence_status
        })

    serializer = StudentPresenceSerializer(student_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

class StudentPointageHistoryView(generics.ListAPIView):
    """
    Vue pour qu'un étudiant puisse voir son historique de pointages.
    """
    serializer_class = PointageSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Pointage.objects.filter(user=self.request.user).order_by('-session__planning__date')
