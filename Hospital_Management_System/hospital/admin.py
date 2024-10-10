from django.contrib import admin
from .models import Doctor , Patient , RejectedDoctors ,Service, DoctorAvailability


admin.site.register([Doctor,Patient,RejectedDoctors,Service,DoctorAvailability])

