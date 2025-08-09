from rest_framework import serializers
from .models import Planning
from users.models import User
from users.serializers import UserSerializer
from module.models import Module
from module.serializers import ModuleSerializers
from horaire.serializers import HoraireSerializer

from horaire.models import Horaire


class PlanningSerializer(serializers.ModelSerializer):
    # Lecture seule : Détail des objets
    module_details = ModuleSerializers(source="module", read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    horaire_details = HoraireSerializer(source="horaire", read_only=True)
    # Champs d’écriture pour module (en ForeignKey)
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all(), allow_null=True)
    horaire = serializers.PrimaryKeyRelatedField(queryset=Horaire.objects.all(), allow_null=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)
    class Meta:
        model = Planning
        fields = "__all__"
        # Cacher l'affichage d'ID de du module dans le JSON

        extra_kwargs = {
            'module': {'write_only': True},
            'user': {'write_only': True},
            'horaire': {'write_only': True}
        }