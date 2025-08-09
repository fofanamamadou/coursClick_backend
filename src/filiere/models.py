from django.db import models

# Create your models here.

#Modele filiere
class Filiere(models.Model) :
    name = models.CharField(max_length=150, blank=False, unique=True)
    description = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.name