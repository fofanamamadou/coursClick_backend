from rest_framework import serializers
from .models import Module
from filiere.serializers import FiliereSerializer
from filiere.models import Filiere
from classe.models import Classe

from classe.serializers import ClasseSerializers


class ModuleSerializers(serializers.ModelSerializer) :

    # Pour voir les détails des filières (en lecture)
    filieres_details = FiliereSerializer(source="filieres", many=True, read_only=True)

    # Pour créer/modifier avec des IDs
    filieres = serializers.PrimaryKeyRelatedField(
        queryset=Filiere.objects.all(),
        many=True
    )
    # Pour voir les détails des classes (en lecture)
    classe_details = ClasseSerializers(source="classe", read_only=True)

    # Pour créer/modifier avec des IDs
    classe = serializers.PrimaryKeyRelatedField(queryset=Classe.objects.all(), allow_null=True)

    class Meta :
        model = Module
        fields = '__all__'
