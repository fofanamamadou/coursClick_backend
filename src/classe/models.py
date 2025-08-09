from django.db import models
from filiere.models import Filiere

# Create your models here.

#Modele classe
class Classe (models.Model) :
    name = models.CharField(max_length=150, blank=False, unique=True)
    description = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.name