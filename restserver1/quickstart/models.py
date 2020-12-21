from django.db import models
from django.urls import reverse

# Create your models here.
class SensorData(models.Model) :
    submit_date = models.DateField(auto_now_add=True)
    station = models.CharField(max_length=100, blank=True, default=' ')
    tpm = models.CharField(max_length=100, blank=True, default=' ')
    temp = models.CharField(max_length=100, blank=True, default=' ')


class EModel(models.Model):
    start = models.DateField(blank=False)
    end = models.DateField(blank=False)