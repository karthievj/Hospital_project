from django.db import models
from django.contrib.auth.models import User
import random

# Doctor Model
class Doctor(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    specialization = models.CharField(max_length=40)
    doctor_id = models.CharField(max_length=10,unique=True,blank=True)
    approval = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

# Patient Model
class Patient(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    age = models.IntegerField()
    mobile_number = models.IntegerField()
    patient_id = models.CharField(max_length=10,unique=True,blank=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
