from rest_framework import serializers

from .models import User
from role.models import Role
from role.serializers import RoleSerializer
from filiere.models import Filiere
from filiere.serializers import FiliereSerializer
from classe.models import Classe
from module.models import Module
from classe.serializers import ClasseSerializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        try:
            # Tenter la validation par défaut
            data = super().validate(attrs)
        except AuthenticationFailed as e:
            # En cas d'échec, personnaliser la réponse d'erreur
            user = User.objects.filter(email=attrs.get(self.username_field)).first()

            error_data = {}
            
            # Si l'utilisateur existe mais est inactif
            if user and not user.is_active:
                error_data['detail'] = "Votre compte a été désactivé. Veuillez contacter l'administrateur."
                error_data['code'] = "account_disabled"
            # Pour toute autre raison (utilisateur non trouvé, mot de passe incorrect)
            else:
                error_data['detail'] = "L'adresse e-mail ou le mot de passe est incorrect."
                error_data['code'] = "invalid_credentials"
            
            # Lever une exception de validation pour retourner une réponse structurée
            raise serializers.ValidationError(error_data)

        # Ajouter les données personnalisées à la réponse si la validation réussit
        data['roles'] = [role.name for role in self.user.roles.all()]
        data['email'] = self.user.email
        data['user_id'] = self.user.id
        
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajouter les rôles au token
        token['roles'] = [role.name for role in user.roles.all()]

        # Facultatif : ajouter d'autres infos utiles
        token['email'] = user.email
        token['user_id'] = user.id

        return token

# Cette classe permet de transformer le model-USER en JSON, vise vers ça
class UserSerializer(serializers.ModelSerializer):
    # Lecture seule : Détail des objets
    filiere_details = FiliereSerializer(source="filiere", read_only=True)
    classe_details = ClasseSerializers(source="classe", read_only=True)
    roles_details = RoleSerializer(source="roles", many=True, read_only=True)

    # Champs d’écriture pour filière et classe (en ForeignKey)
    filiere = serializers.PrimaryKeyRelatedField(queryset=Filiere.objects.all(), allow_null=True)
    classe = serializers.PrimaryKeyRelatedField(queryset=Classe.objects.all(), allow_null=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), allow_null=True)


    #ManyToMany

    modules = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        # Lier notre model User à la classe
        model = User
        # Les champs que nous souhaitons utiliser dans le formulaire
        fields = "__all__"
        # Cacher l'affichage du mot de passe dans le JSON
        extra_kwargs = {
            'password': {'write_only': True},

        }




    # Hachage le mot de passe de l'utilisateur
    def create(self, validated_data):
        # Extraire le mot de passe
        extracted_password = validated_data.pop('password', None)
        # Extraire les rôles (ManyToMany)
        roles_data = validated_data.pop('roles', [])
        # Extraire les modules (ManyToMany)
        modules_data = validated_data.pop('modules', [])

        # Supprimer les M2M hérités de PermissionsMixin (cause l'erreur 'Direct assignment to the forward side of a many-to-many set is prohibited' )
        validated_data.pop('groups', None)
        validated_data.pop('user_permissions', None)

        # Créer l'utilisateur
        user_instance = self.Meta.model(**validated_data)

        # Vérifier si le mot de passe n'est pas null
        if extracted_password is not None:
            user_instance.set_password(extracted_password)

        # Sauvegarder l'utilisateur
        user_instance.save()

        # Associer les rôles après la sauvegarde
        user_instance.roles.set(roles_data)
        # Associer les modules après la sauvegarde
        user_instance.modules.set(modules_data)

        return user_instance


    # Token personnalisee pour y extraire des infos






