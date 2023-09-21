from django.db import models

# Create your models here.

class FormData(models.Model):
    is_pulmonary_TB = models.BooleanField(default=False)
    has_solid_organ_malignancy = models.BooleanField(default=False)
    is_galactomannan_positive = models.BooleanField(default=False)
    is_receiving_systemic_corticosteroids = models.BooleanField(default=False)

class IPAPrediction(models.Model):
    ipa_prob = models.FloatField() 
    total_score = models.IntegerField()  
    form_data = models.ForeignKey(FormData, on_delete=models.CASCADE)