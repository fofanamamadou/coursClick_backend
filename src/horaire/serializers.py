from rest_framework import serializers
from .models import Horaire
from module.models import Module
from module.serializers import ModuleSerializers

class HoraireSerializer(serializers.ModelSerializer):
    # Lecture seule : Détail des objets
    module_details = ModuleSerializers(source="module", read_only=True)
    # Champs d’écriture pour module (en ForeignKey)
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all(), allow_null=True)
    class Meta:
        model = Horaire
        fields = "__all__"
        # Cacher l'affichage d'ID de du module dans le JSON

        extra_kwargs = {
            'module': {'write_only': True}
        }