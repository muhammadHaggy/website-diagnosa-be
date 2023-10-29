from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class FormData(models.Model):
    is_pulmonary_TB = models.BooleanField(default=False)
    has_solid_organ_malignancy = models.BooleanField(default=False)
    is_galactomannan_positive = models.BooleanField(default=False)
    is_receiving_systemic_corticosteroids = models.BooleanField(default=False)
    is_probable = models.BooleanField(default=False)

class IPAPrediction(models.Model):
    ipa_prob = models.FloatField() 
    total_score = models.IntegerField()  
    form_data = models.ForeignKey(FormData, on_delete=models.CASCADE)
    is_probable = models.BooleanField(default=False)
    is_high_risk = models.BooleanField(default=False)
    submission_date = models.DateTimeField(default=timezone.now)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="predictions", default=None)
