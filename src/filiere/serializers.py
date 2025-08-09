# Cette classe permet de tranformer le Model(Absence) en JSON, vise vers ça
from rest_framework import serializers
from .models import Filiere

class FiliereSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Filiere
        fields = "__all__"