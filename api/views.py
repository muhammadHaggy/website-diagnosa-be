from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import FormData, IPAPrediction
from .serializers import FormDataSerializer, PredDataSerializer

@api_view(['GET'])
def getData(request):
    items = FormData.objects.all()
    serializer = FormDataSerializer(items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getPred(request):
    if request.user.is_authenticated and request.user.groups.filter(name='Admin').exists():
        items = IPAPrediction.objects.all()
        serializer = PredDataSerializer(items, many=True)
        return Response(serializer.data)
    return Response({"detail": "Permission Denied"}, status=403)

@api_view(['POST'])
def addData(request):
    serializer = FormDataSerializer(data=request.data)
    if serializer.is_valid():
        response = calculateIpaPred(request)
    return Response(response.data)

def calculateIpaPred(request):
    serializer = FormDataSerializer(data=request.data)
    proba_list = [10.4, 14.8, 20.6, 28.0, 36.8, 46.6, 56.6, 66.1]
    score = 0
    if serializer.is_valid():
        validated_data = serializer.validated_data
        is_probable = validated_data.get('is_probable')
        is_pulmonary_TB = validated_data.get('is_pulmonary_TB')
        has_solid_organ_malignancy = validated_data.get('has_solid_organ_malignancy')
        is_galactomannan_positive = validated_data.get('is_galactomannan_positive')
        is_receiving_systemic_corticosteroids = validated_data.get('is_receiving_systemic_corticosteroids')
        if is_pulmonary_TB:
            score += 2
        if has_solid_organ_malignancy:
            score += 2
        if is_galactomannan_positive:
            score += 2
        if is_receiving_systemic_corticosteroids:
            score += 1
    ipa_proba = proba_list[score]
    form_data_instance = serializer.save()
    is_high_risk = False
    if (score >= 2):
        is_high_risk = True
    else:
        is_high_risk = False
    ipa_pred_instance = IPAPrediction.objects.create(
        is_high_risk = is_high_risk,
        is_probable = is_probable,
        ipa_prob = ipa_proba,
        total_score = score,
        form_data = form_data_instance
    )
    ipa_pred_instance.save()
    return PredDataSerializer(ipa_pred_instance)

from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['POST'])
def register_basic_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    
    if not username or not password or not email:
        return JsonResponse({'error': 'Missing credentials'}, status=400)
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)
    
    user = User.objects.create_user(username=username, password=password, email=email)
    
    # Add user to the Basic User group
    basic_user_group = Group.objects.get(name='Basic User')
    basic_user_group.user_set.add(user)
    
    return JsonResponse({'message': 'User registered successfully'}, status=201)

from django.contrib.auth import authenticate, login
from django.http import JsonResponse

@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        
        # Retrieve user roles (groups)
        roles = [group.name for group in user.groups.all()]

        return JsonResponse({'message': 'Logged in successfully', 'roles': roles}, status=200)
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
