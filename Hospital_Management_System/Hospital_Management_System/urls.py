
from django.contrib import admin
from django.urls import path ,include
from hospital import views

urlpatterns = [
    #admin urls
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('dashboard/',views.dashboard,name="dashboard"),

    #doctor urls
    path('register_doctor/',views.register_doctor, name="register_doctor"),
    path('doctor_login/',views.doctor_login,name="doctor_login"),
    path('doctor_approve/<str:id>/',views.doctor_approve,name="doctor_approve"),
    path('doctor_reject/<str:id>/',views.doctor_reject,name="doctor_reject"),

    #patient urls
    path('register_patient/',views.register_patient,name="register_patient"),

]
