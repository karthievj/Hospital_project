from django.db import models
from django.contrib.auth.models import User
import random ,string

# Doctor Model
class Doctor(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE) 
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    specialization = models.CharField(max_length=40)
    doctor_id = models.CharField(max_length=10,unique=True,blank=True)
    passwd = models.CharField(max_length=50)
    approval = models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        """DOCTOR ID : DO{first 1 letter of the firstname and 
        first 1 letter of last name with random 4 digit}
        Eg - First name -  Suresh
            Last name - Kannan

            Doctor id - DOSK8754
        """

        if not self.doctor_id:
            first_name = self.first_name
            last_name = self.last_name
            pre1 = first_name[:1]
            pre2 = last_name[:1]
            random_id = ''.join(random.choices(string.digits,k=4)) 
            self.doctor_id = f"DO{pre1.upper()}{pre2.upper()}{random_id}"
        super().save(*args,**kwargs)
        
    def __str__(self) -> str:
        return f"{self.first_name}_{self.last_name}"

# Patient Model
class Patient(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    age = models.IntegerField()
    mobile_number = models.IntegerField()
    passwd = models.CharField(max_length=50)
    patient_id = models.CharField(max_length=10,unique=True,blank=True)

    def save(self,*args,**kwargs):
        """Patient ID : PT{first 1 letter of the firstname and 
        first 1 letter of last name with random 4 digit}
        Eg - First name -  Suresh
            Last name - Kannan

            Patient id - PATSK1234
        """

        if not self.patient_id:
            first_name = self.first_name
            last_name = self.last_name
            pre1 = first_name[:1]
            pre2 = last_name[:1]
            random_id = ''.join(random.choices(string.digits,k=4)) 
            self.patient_id = f"PAT{pre1.upper()}{pre2.upper()}{random_id}"
        super().save(*args,**kwargs)

    def __str__(self) -> str:
        return f"{self.first_name}_{self.last_name}"
    
class RejectedDoctors(models.Model):
    doctor_id = models.CharField(max_length=10,unique=True,blank=True)
    username= models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.doctor_id}"
    
class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    available_date = models.DateField()

    class Meta:
        unique_together = ('doctor', 'available_date')

    def __str__(self):
        return f"{self.doctor.first_name} - {self.available_date}"
    
class Service(models.Model): # admin
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ${self.cost}"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    services = models.ManyToManyField(Service)  # Link to the Service model
    appt_id = models.CharField(max_length=10,unique=True,blank=True)
    appt_status = models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        """Appoitment ID : APPT362523
        Eg - Date -  01/10/24
            Appt id - APPT011034
        """
        if not self.appt_id:
            appt_date = self.appointment_date.strftime('%d%m') # 0110
            random_id = ''.join(random.choices(string.digits,k=2)) 
            self.appt_id = f"APPT{appt_date}{random_id}"
        super().save(*args,**kwargs)

    def __str__(self):
        return f"Appointment {self.appt_id} with Dr. {self.doctor.first_name} for {self.patient.first_name}"



