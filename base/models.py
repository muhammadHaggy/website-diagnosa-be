from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

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

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
