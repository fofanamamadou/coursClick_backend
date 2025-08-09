from django.db import models
from filiere.models import Filiere
from classe.models import Classe


# Create your models here.
class Module(models.Model) :
    name = models.CharField(max_length=150, blank=False)
    description = models.TextField(max_length=255, blank=True)
    session=models.TextField(max_length=2, blank=True)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, related_name="modules")
    filieres = models.ManyToManyField(Filiere, related_name="modules", blank=True)

    def __str__(self):
        return self.name
