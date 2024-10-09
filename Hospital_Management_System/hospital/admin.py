from django.contrib import admin
from .models import Doctor , Patient , RejectedDoctors


admin.site.register([Doctor,Patient,RejectedDoctors])


