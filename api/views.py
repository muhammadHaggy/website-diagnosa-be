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
from base.models import Profile

@api_view(['POST'])
def register_basic_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    first_name = request.data.get('first_name')  
    last_name = request.data.get('last_name')  
    age = request.data.get('age')  

    if not username or not password or not email or not first_name or not last_name or age is None:
        return Response({'error': 'Missing credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create the user
    user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
    
    # Create the profile with the age
    profile = Profile.objects.create(user=user, age=age)
    
    # Add user to the Basic User group
    basic_user_group = Group.objects.get(name='Basic User')
    basic_user_group.user_set.add(user)
    
    token, created = Token.objects.get_or_create(user=user)
    roles = [group.name for group in user.groups.all()]
    
    return Response({'token': token.key, 'message': 'User registered successfully', 'roles': roles, 'age': profile.age}, status=status.HTTP_201_CREATED)



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


from django.utils import timezone
from django.db.models.functions import TruncWeek
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import IPAPrediction
from datetime import timedelta

@api_view(['GET'])
def chart_data(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name='Admin').exists():
        return Response({"detail": "Permission Denied"}, status=403)
    
    # Counter for is_probable and is_high_risk
    is_probable_count = IPAPrediction.objects.filter(is_probable=True).count()
    is_high_risk_count = IPAPrediction.objects.filter(is_high_risk=True).count()
    
    # Total count of IPA predictions
    total_ipa_predictions = IPAPrediction.objects.count()

    # # Get the earliest submission date from IPAPredictions, or use current time if none exist
    # earliest_submission = IPAPrediction.objects.earliest('submission_date').submission_date if IPAPrediction.objects.exists() else timezone.now()


    # Query the actual submission counts
    submissions_by_week = IPAPrediction.objects\
                                                .annotate(week=TruncWeek('submission_date'))\
                                                .values('week')\
                                                .annotate(count=Count('id'))\
                                                .order_by('week')
    
    # get the earlist submission week date in submissions_by_week
    earliest_submission_week = submissions_by_week[0]['week'].date() if submissions_by_week else timezone.now().date()


    # Start the chart from one week before the earliest submission
    start_date = earliest_submission_week - timedelta(weeks=1)

    # get submissions_by_week count
    submissions_by_week_count = len(submissions_by_week)

    # Create the range of weeks for the chart data
    weeks = [(start_date - timedelta(days=i)) for i in range(0, (10-submissions_by_week_count)*7, 7)]

    # reverse the list so that the weeks are in ascending order
    weeks.reverse()

    # Create a dictionary of submissions by week with default count 0
    submissions_dict = {week: 0 for week in weeks}
    
    # Update the dictionary with actual counts
    for submission in submissions_by_week:
        week = submission['week'].date()
        submissions_dict[week] = submission['count']
    
    # Convert the dictionary back to a list of dictionaries
    submissions_list = [{'week': week, 'count': count} for week, count in submissions_dict.items()]

    data = {
        'is_probable_count': is_probable_count,
        'is_high_risk_count': is_high_risk_count,
        'total_ipa_predictions': total_ipa_predictions,
        'submissions_by_week': submissions_list,
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

# views.py
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django_ratelimit.decorators import ratelimit
# from .models import IPAPrediction, FormData

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate='1/m', block=True, method='POST')
def send_email_to_submitter(request, prediction_id):
    # Retrieve the IPAPrediction instance by ID
    prediction = get_object_or_404(IPAPrediction, id=prediction_id)

    # Check if submitted_by is not None and if the request user is the submitter
    if prediction.submitted_by is None:
        return HttpResponse("This prediction was submitted anonymously and has no associated email.", status=400)

    if prediction.submitted_by != request.user:
        return HttpResponse("Permission Denied: You can only send emails for predictions you submitted.", status=403)

    # Get the submitter's email
    submitter_email = prediction.submitted_by.email

    # Retrieve the FormData instance
    form_data = prediction.form_data

     # Retrieve and format reported symptoms
    symptoms = []
    if form_data.is_pulmonary_TB: symptoms.append("Pulmonary TB")
    if form_data.has_solid_organ_malignancy: symptoms.append("Solid Organ Malignancy")
    if form_data.is_galactomannan_positive: symptoms.append("Galactomannan Positive")
    if form_data.is_receiving_systemic_corticosteroids: symptoms.append("Receiving Systemic Corticosteroids")
    symptoms_list = ", ".join(symptoms)

    # Define email content
    subject = 'Hasil Form Diagnosa'
    from_email = 'no-reply@mikostop.com'  # Replace with your email

    # Define context data for the template
    context = {
        'patient_first_name': prediction.submitted_by.username,
        'symptoms_list': symptoms_list,
        'total_score': prediction.total_score,
        'risk_level': "High" if prediction.is_high_risk else "Low",
        'ipa_prob': prediction.ipa_prob,
        'prediction_id': prediction.id
    }

    # Load and render the email template
    html_content = render_to_string('email_template.html', context)

    # Create an email message
    msg = EmailMultiAlternatives(subject, html_content, from_email, [submitter_email])
    msg.attach_alternative(html_content, "text/html")

    # Send email
    msg.send()

    return HttpResponse("Email sent successfully")