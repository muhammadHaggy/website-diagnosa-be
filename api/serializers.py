from rest_framework import serializers
from base.models import FormData,IPAPrediction

class FormDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormData
        fields = '__all__'

from rest_framework import serializers
from base.models import FormData, IPAPrediction, Profile
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'age']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']  # Add 'profile' to include the related Profile data

class PredDataSerializer(serializers.ModelSerializer):
    submitted_by = UserSerializer(read_only=True)  # Ensure 'submitted_by' is read-only if it's not intended to be set by the serialized data

    class Meta:
        model = IPAPrediction
        fields = '__all__'
