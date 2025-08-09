# Cette classe permet de tranformer le Model(Role) en JSON, vise vers ça
from rest_framework import serializers
from .models import Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        # Lier le model Role
        model = Role
        # Les champs que nous souhaitons utiliser dans le formulaire
        fields = "__all__"