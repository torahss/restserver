from django.contrib.auth.models import User, Group
from rest_framework import serializers
from quickstart.models import SensorData

class SensorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SensorData
        fields = ('submit_date', 'station', 'tpm', 'temp')
