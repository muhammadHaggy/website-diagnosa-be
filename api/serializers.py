from rest_framework import serializers
from base.models import FormData,IPAPrediction

class FormDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormData
        fields = '__all__'

class PredDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPAPrediction
        fields = '__all__'