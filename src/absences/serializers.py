from rest_framework import serializers
from .models import Absence
from users.serializers import UserSerializer # Pour afficher les détails de l'utilisateur

class AdminAbsenceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les administrateurs. Affiche tous les champs, y compris les détails de l'utilisateur.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Absence
        fields = [
            'id',
            'user',
            'planning',
            'statut',
            'justificatif_texte',
            'justificatif_document',
            'cree_le',
            'modifie_le'
        ]

class StudentAbsenceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les étudiants. N'affiche que les informations pertinentes pour eux.
    """
    class Meta:
        model = Absence
        fields = [
            'id',
            'planning',
            'statut',
            'justificatif_texte',
            'justificatif_document',
            'cree_le'
        ]
        read_only_fields = ['statut', 'planning', 'cree_le']


class StudentJustificationSerializer(serializers.ModelSerializer):
    """
    Serializer utilisé par l'étudiant pour soumettre ou mettre à jour un justificatif.
    """
    class Meta:
        model = Absence
        fields = ['justificatif_texte', 'justificatif_document']

    def update(self, instance, validated_data):
        # Quand un étudiant soumet un justificatif, le statut passe automatiquement à "En attente"
        instance.justificatif_texte = validated_data.get('justificatif_texte', instance.justificatif_texte)
        instance.justificatif_document = validated_data.get('justificatif_document', instance.justificatif_document)
        
        # On vérifie qu'au moins un des deux champs de justification est rempli
        if not instance.justificatif_texte and not instance.justificatif_document:
            raise serializers.ValidationError("Vous devez fournir au moins un texte ou un document de justification.")

        instance.statut = 'EN_ATTENTE'
        instance.save()
        return instance
