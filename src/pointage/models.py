from django.db import models
from django.conf import settings
from planning.models import Planning  # Assurez-vous que le nom de l'app et du modèle sont corrects

class SessionPresence(models.Model):
    """
    Représente une session d'appel lancée par un professeur.
    """
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name='sessions_presence')
    code = models.CharField(max_length=10, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Session pour {self.planning} - Code: {self.code}"

class Pointage(models.Model):
    """
    Enregistre la présence d'un étudiant à une session de cours.
    """
    session = models.ForeignKey(SessionPresence, on_delete=models.CASCADE, related_name='pointages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pointages')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Assure qu'un étudiant ne peut pointer qu'une seule fois par session
        unique_together = ('session', 'user')

    def __str__(self):
        return f"Pointage de {self.user.username} pour la session {self.session.id}"