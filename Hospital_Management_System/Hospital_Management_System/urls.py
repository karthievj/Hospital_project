
from django.contrib import admin
from django.urls import path ,include
from hospital import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('register_doctor/',views.register_doctor, name="register_doctor"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('doctor_login/',views.doctor_login,name="doctor_login")
]
