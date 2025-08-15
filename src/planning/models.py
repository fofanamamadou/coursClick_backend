from django.db import models
from users.models import User
from horaire.models import Horaire

# Create your models here.

class Planning(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="plannings")
    horaire = models.ForeignKey(Horaire, on_delete=models.SET_NULL, null=True, related_name="plannings")
    date = models.DateField(blank=False)
    date_creation = models.DateField(auto_now_add=True)
    is_validated_by_professor = models.BooleanField(default=False)
    is_validated_by_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.horaire} ({self.date})"

    @property
    def module(self):
        """Récupère automatiquement le module lié via l'horaire"""
        return self.horaire.module if self.horaire else None
