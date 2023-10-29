from rest_framework import serializers
from base.models import FormData,IPAPrediction

class FormDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormData
        fields = '__all__'

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class PredDataSerializer(serializers.ModelSerializer):
    submitted_by = UserSerializer()

    class Meta:
        model = IPAPrediction
        fields = '__all__'
