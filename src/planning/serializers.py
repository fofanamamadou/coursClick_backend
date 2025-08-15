from rest_framework import serializers
from .models import Planning
from users.models import User
from users.serializers import UserSerializer
from horaire.models import Horaire
from horaire.serializers import HoraireSerializer
from module.serializers import ModuleSerializers

class PlanningSerializer(serializers.ModelSerializer):
    # Lecture seule : détails
    user_details = UserSerializer(source="user", read_only=True)
    horaire_details = HoraireSerializer(source="horaire", read_only=True)
    module_details = ModuleSerializers(source="horaire.module", read_only=True)  # module via horaire

    # Champs d’écriture
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)
    horaire = serializers.PrimaryKeyRelatedField(queryset=Horaire.objects.all(), allow_null=True)

    class Meta:
        model = Planning
        fields = [
            "id",
            "user",
            "horaire",
            "date",
            "date_creation",
            "is_validated_by_professor",
            "is_validated_by_admin",
            "user_details",
            "horaire_details",
            "module_details",
        ]
        extra_kwargs = {
            "user": {"write_only": True},
            "horaire": {"write_only": True},
        }
