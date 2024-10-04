from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Doctor, Patient
from django.contrib.auth import authenticate,login,logout


def home(request):
    return render(request,"home.html")

def dashboard(request):
    unapproved_doctors = Doctor.objects.filter(approval=False).values()
    unapproved_doctors_count = len(unapproved_doctors)
    if unapproved_doctors_count == 0:
        return render(request,"dashboard.html")
    else:
        print(unapproved_doctors,"data")
        data = {'unapproved_doctors':unapproved_doctors,
                'unapproved_doctors_count':unapproved_doctors_count}
        return render(request,"dashboard.html",context=data)

def register_doctor(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        uname = request.POST['uname']
        specialization = request.POST['specialization']
        passwd1 = request.POST['passwd1']
        passwd2 = request.POST['passwd2']

        # password validation
        if passwd1 != passwd2:
            messages.error(request,"Passwords not matched...Plzzz re enter your passeord")
            return redirect("/register_doctor")
        
        # username unique validation
        doctor = User.objects.filter(username=uname).exists()
        if doctor:
            messages.error(request,"Username you typed is already exists..Plzzz choose another username or contact admin panel")
            return redirect("/register_doctor")
        
        # Doctor data Saving
        doctor_user = User.objects.create_user(username=uname, password=passwd1)
        doctor_user.is_active = False  # Disable login until approved
        doctor_user.save()

        doctor = Doctor.objects.create(user=doctor_user, 
                                        first_name = fname,
                                        last_name = lname,
                                        username = uname,
                                        specialization = specialization,
                                        passwd=passwd1)
        messages.success(request, "Your registration is submitted for approval....Plzz check the Doctor login panel for status")
        return redirect('/doctor_login')

    return render(request, "register_doctor.html")

def doctor_login(request):
    if request.method=="POST":
        uname = request.POST['uname']
        passwd = request.POST['passwd']
        user = authenticate(username=uname,password=passwd)
        print(user,"user")
        # user is present or not
        if user is not None:
            # Doctor approval validation
            if hasattr(user,'doctor') and not user.doctor.approval:
                messages.warning(request,"Your doctor registration is waiting for approval")
            # if not hasattr(user,'doctor'):
            #     messages.warning(request,"Your doctor profile is rejected by admin...plzz contact administration")
            else:
                login(request,user)
                # Doctor dashboard 
                return HttpResponse("Hi")
        else:
            messages.error(request,"Invalid login credentials...Plzz check password and username")
            return redirect("/doctor_login")
        
    return render(request, "doctor_login.html")

def doctor_approve(request,id):
    doctor = Doctor.objects.get(doctor_id=id)
    doctor.user.is_active = True # Here apprpoving the user login
    doctor.approval = True # Here only we are approving the doctor
    doctor.user.save() # save for user model
    doctor.save() # save for doctor model
    messages.success(request, f"Doctor {doctor.first_name} {doctor.last_name} approved successfully")
    return redirect('/dashboard')

def doctor_reject(request,id):
    doctor = Doctor.objects.get(doctor_id=id)
    doctor.user.delete() # 
    doctor.delete()    

def register_patient(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        age = request.POST['age']

        user = User.objects.create_user(username=username, password=password)
        user.is_active = True  # Disable login until approved
        user.save()

        patient = Patient.objects.create(user=user, name=name, age=age)
        messages.success(request, "Your registration is submitted for approval.")
        return redirect('/home')

    return render(request, 'register_patient.html')

def patient_login(request):
    return HttpResponse("Patient Login view")
