from rest_framework import serializers


from .models import Classe


class ClasseSerializers(serializers.ModelSerializer) :

    class Meta:
        model = Classe
        fields = '__all__'