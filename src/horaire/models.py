from django.db import models
from module.models import Module


# Create your models here.
class Horaire(models.Model) :
    time_start_course=models.TimeField(blank=False)
    time_end_course=models.TimeField(blank=False)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, related_name="horaires")
    jours = models.CharField(max_length=8, blank=False)
    salle = models.CharField(max_length=50, blank=False, null=True)


    def __str__(self):
        return self.salle