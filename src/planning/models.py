from django.db import models
from users.models import User
from module.models import Module
from horaire.models import Horaire

# Create your models here.

class Planning(models.Model) :
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="planning")
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, related_name="planning")
    horaire = models.ForeignKey(Horaire, on_delete=models.SET_NULL, null=True, related_name="planning")
    date = models.DateField(blank=False)
    date_creation = models.DateField(blank=False, auto_now_add=True)
    his_state = models.BooleanField(default=False)
    validate = models.BooleanField(default=False)


