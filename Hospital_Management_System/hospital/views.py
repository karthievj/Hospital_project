from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Doctor, Patient , RejectedDoctors
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
            messages.warning(request,"Passwords not matched...Plzzz re enter your passeord")
            return redirect("/register_doctor")
        
        # username unique validation
        doctor = User.objects.filter(username=uname).exists()
        if doctor:
            messages.warning(request,"Username you typed is already exists..Plzzz choose another username or contact admin panel")
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
        reject_obj = RejectedDoctors.objects.filter(username=uname).exists()
        print(reject_obj)
        if reject_obj==False:   #Doctor Rejection validation
            if user is not None: # User validation
                if hasattr(user,'doctor') and not user.doctor.approval: # Doctor approval validation
                    messages.warning(request,"Your doctor registration is waiting for approval")
                else:
                    login(request,user)
                    # Doctor dashboard 
                    return HttpResponse("Hi")
            else:
                messages.error(request,"Your application is still in pending state..Plzz contact admin panel")
        else:
            messages.error(request,"Your application is rejected by the admin...")
            return redirect("/doctor_login")
        
    return render(request, "doctor_login.html")

def doctor_approve(request,id):
    doctor = Doctor.objects.get(doctor_id=id)
    doctor.user.is_active = True # Here apprpoving the user login
    doctor.approval = True # Here only we are approving the doctor
    doctor.user.save() # save for user model
    doctor.save() # save for doctor model
    unapproved_doctors = Doctor.objects.filter(approval=False).values() #database
    unapproved_doctors_count = len(unapproved_doctors)
    msg = {'approve_message':f"Doctor {doctor.first_name} {doctor.last_name} approved successfully"}
    if unapproved_doctors_count == 0:
        return render(request,"dashboard.html",context=msg)
    else:
        print(unapproved_doctors,"data")
        data = {'unapproved_doctors':unapproved_doctors,
                'unapproved_doctors_count':unapproved_doctors_count,
                'approve_message':f"Doctor {doctor.first_name} {doctor.last_name} approved successfully"}
        return render(request,"dashboard.html",context=data)

def doctor_reject(request,id):
    doctor = Doctor.objects.get(doctor_id=id)
    firt_name = doctor.first_name
    last_name = doctor.last_name
    doctor_id = doctor.doctor_id
    username = doctor.username
    RejectedDoctors.objects.create(
        doctor_id = doctor_id,
        username = username
    )
    doctor.user.delete() 
    doctor.delete()
    unapproved_doctors = Doctor.objects.filter(approval=False).values() #database
    unapproved_doctors_count = len(unapproved_doctors)
    msg = {'delete_message':f"Doctor {firt_name} {last_name} rejected"}
    if unapproved_doctors_count == 0:
        return render(request,"dashboard.html",context=msg)
    else:
        print(unapproved_doctors,"data")
        data = {'unapproved_doctors':unapproved_doctors,
                'unapproved_doctors_count':unapproved_doctors_count,
                'approve_message':f"Doctor {firt_name} {last_name} rejected"}
        return render(request,"dashboard.html",context=data)

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
