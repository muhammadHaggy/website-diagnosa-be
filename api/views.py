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
    items = IPAPrediction.objects.all()
    serializer = PredDataSerializer(items, many=True)
    return Response(serializer.data)

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
