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
        form_data = form_data_instance,
        submitted_by = request.user if request.user.is_authenticated else None
    )
    ipa_pred_instance.save()
    return PredDataSerializer(ipa_pred_instance)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group

@api_view(['POST'])
def register_basic_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    
    if not username or not password or not email:
        return Response({'error': 'Missing credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, password=password, email=email)
    
    # Add user to the Basic User group
    basic_user_group = Group.objects.get(name='Basic User')
    basic_user_group.user_set.add(user)
    
    token, created = Token.objects.get_or_create(user=user)
    roles = [group.name for group in user.groups.all()]
    
    return Response({'token': token.key, 'message': 'User registered successfully', 'roles': roles}, status=status.HTTP_201_CREATED)


from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        roles = [group.name for group in user.groups.all()]
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'message': 'Logged in successfully', 'roles': roles}, status=status.HTTP_200_OK)
    else:
        return Response({'error':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import IPAPrediction

from django.db.models.functions import TruncWeek

@api_view(['GET'])
def chart_data(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='Admin').exists():
        return Response({"detail": "Permission Denied"}, status=403)
    
    # Counter for is_probable and is_high_risk
    is_probable_count = IPAPrediction.objects.filter(is_probable=True).count()
    is_high_risk_count = IPAPrediction.objects.filter(is_high_risk=True).count()
    
    # Line chart data for form submissions grouped by week
    submissions_by_week = IPAPrediction.objects.annotate(week=TruncWeek('submission_date'))\
                                               .values('week')\
                                               .annotate(count=Count('id'))\
                                               .order_by('week')

    data = {
        'is_probable_count': is_probable_count,
        'is_high_risk_count': is_high_risk_count,
        'submissions_by_week': list(submissions_by_week),
    }

    return Response(data)



@api_view(['GET'])
def score_distribution(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='Admin').exists():
        return Response({"detail": "Permission Denied"}, status=403)
    # Getting the count of predictions for each score
    score_counts = IPAPrediction.objects.values('total_score').annotate(count=Count('id')).order_by('total_score')
    
    data = {
        'score_distribution': list(score_counts)
    }

    return Response(data)

@api_view(['GET'])
def probability_distribution(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='Admin').exists():
        return Response({"detail": "Permission Denied"}, status=403)
    
    # Getting the count of predictions for each probability
    prob_counts = IPAPrediction.objects.values('ipa_prob').annotate(count=Count('id')).order_by('ipa_prob')
    
    data = {
        'probability_distribution': list(prob_counts)
    }

    return Response(data)
