from rest_framework import serializers
from .models import SessionPresence, Pointage
from users.serializers import UserSerializer

class SessionPresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPresence
        fields = ('id', 'planning', 'code', 'end_time', 'is_active')

class CreateSessionPresenceSerializer(serializers.Serializer):
    planning_id = serializers.IntegerField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class ValidatePresenceSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class PointageSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    session = SessionPresenceSerializer()

    class Meta:
        model = Pointage
        fields = ('id', 'user', 'session', 'timestamp')

class StudentPresenceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    classe = serializers.CharField()
    filiere = serializers.CharField()
    status = serializers.CharField()
