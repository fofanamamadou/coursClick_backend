from django.db import models
from users.models import User
from planning.models import Planning

class Absence(models.Model):
    """
    Représente une absence d'un étudiant à une session de cours spécifique.
    Une absence est générée automatiquement si aucun pointage n'est trouvé pour l'étudiant
    à la fin de la session de cours.
    """
    STATUT_CHOICES = [
        ('NON_JUSTIFIEE', 'Non justifiée'),
        ('EN_ATTENTE', 'En attente de validation'),
        ('APPROUVEE', 'Approuvée'),
        ('REFUSEE', 'Refusée'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='absences',
        limit_choices_to={'roles__name': 'STUDENT'} # S'assure que seul un étudiant peut avoir une absence
    )
    planning = models.ForeignKey(
        Planning,
        on_delete=models.CASCADE,
        related_name='absences'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='NON_JUSTIFIEE'
    )
    justificatif_texte = models.TextField(
        blank=True,
        null=True,
        help_text="Texte de justification soumis par l'étudiant."
    )
    justificatif_document = models.FileField(
        upload_to='justificatifs_absences/',
        blank=True,
        null=True,
        help_text="Document (PDF, image) soumis par l'étudiant."
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        # Un étudiant ne peut pas être absent deux fois pour le même cours
        unique_together = ('user', 'planning')
        ordering = ['-cree_le']

    def __str__(self):
        return f"Absence de {self.user.email} pour le cours du {self.planning.date}"