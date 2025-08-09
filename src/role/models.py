from django.db import models

# Create your models here.

#Modele filiere
class Role(models.Model) :
    name = models.CharField(max_length=15, blank=False, unique=True)

    def __str__(self):
        return self.name