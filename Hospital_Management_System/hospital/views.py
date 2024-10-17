from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Doctor, Patient , RejectedDoctors , DoctorAvailability , Service , Appointment
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required 
from datetime import date, timedelta , datetime
from django.http import JsonResponse
from django.db.models import Exists, OuterRef


def home(request):
    return render(request,"home.html")

##################### Admin views #################################################
@login_required
def dashboard(request):
    if request.user.is_superuser:
        unapproved_doctors = Doctor.objects.filter(approval=False).values()
        unapproved_doctors_count = len(unapproved_doctors)
        if unapproved_doctors_count == 0:
            return render(request,"dashboard.html")
        else:
            print(unapproved_doctors,"data")
            data = {'unapproved_doctors':unapproved_doctors,
                    'unapproved_doctors_count':unapproved_doctors_count}
            return render(request,"dashboard.html",context=data)
    else:
        messages.error(request, "You're not a admin user")
        return redirect('admin_login')

@login_required
def all_doctor(request):
    if request.user.is_superuser:
        return render(request,"all_doctor.html")
    else:
        messages.error(request, "You're not a admin user")
        return redirect('admin_login')

def admin_login(request):
    if request.method == "POST":
        uname = request.POST['uname']
        passwd = request.POST['passwd']
        user = authenticate(username=uname, password=passwd)
        
        if user is not None and user.is_superuser:
            login(request, user)
            request.session['is_logged_in'] = True 
            return redirect('dashboard')  # Redirect to the admin dashboard
        else:
            messages.error(request, "Invalid credentials or not an admin.")
    return render(request, 'admin_login.html')

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
    
#################################### Doctor views ####################################
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
        if reject_obj==False:   #Doctor Rejection validation
            if user is not None: # User validation
                if hasattr(user,'doctor') and not user.doctor.approval: # Doctor approval validation
                    messages.warning(request,"Your doctor registration is waiting for approval")
                else:
                    login(request,user)
                    doctor_obj = Doctor.objects.get(username=uname)

                    # Store doctor details in session
                    request.session['doctor_id'] = doctor_obj.doctor_id
                    request.session['doctor_name'] = doctor_obj.first_name 
                    request.session['is_logged_in'] = True 

                    messages.success(request,"Logged in successfully...")
                    return redirect("doctor_dashboard")
            else:
                messages.error(request,"Invalid login Credential")
        else:
            messages.error(request,"Your application is rejected by the admin...")
            return redirect("/doctor_login")
        
    return render(request, "doctor_login.html")

def set_availability(request,id):
    doctor = request.user.doctor
    if request.method=="POST":
        availability_dates = request.POST.getlist('availability_dates')
        for date_str in availability_dates:
            available_date = datetime.strptime(date_str,"%b. %d, %Y").date()
            DoctorAvailability.objects.get_or_create(doctor=doctor,available_date=available_date) # duplicate
        messages.success(request,"Your availability for this week is updated")
        return redirect('doctor_dashboard')
    else:
        return redirect('doctor_dashboard')

def doctor_dashboard(request):
    doctor_id = request.session.get('doctor_id')
    today = date.today()
    next_week_dates = [today + timedelta(days=i) for i in range(7)]  # List of the next 7 days
    
    if doctor_id:
        # Retrieve the doctor object
        doctor_obj = Doctor.objects.get(doctor_id=doctor_id)
        data = {
            "doctor_obj": doctor_obj,
            "next_week_dates": next_week_dates,
        }
        return render(request, "doctor_dashboard.html", context=data)
    else:
        messages.warning(request,'Doctor is not logged in..')
        # If no doctor in session, redirect to login
        return redirect("doctor_login")

def doctor_appointments(request):
    if request.user.is_authenticated:
        doctor = request.user.doctor
        doct_appt_obj = Appointment.objects.filter(doctor=doctor).order_by('appointment_date') # Ascending
        
        context = {
            'doct_appt_obj':doct_appt_obj,
            'doctor':doctor
        }
        return render(request,"doctor_appointments.html",context)
    else:
        messages.error(request,"Session expired...")
        return redirect("doctor_login")




############################### Patient Views ###############################
def register_patient(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        uname = request.POST['uname']
        age = request.POST['age']
        mobile = request.POST['mobile']
        passwd1 = request.POST['passwd1']
        passwd2 = request.POST['passwd2']

        # password validation
        if passwd1 != passwd2:
            messages.warning(request,"Passwords not matched...Plzzz re enter your passeord")
            return redirect("register_patient")
        
        # username unique validation
        doctor = User.objects.filter(username=uname).exists()
        if doctor:
            messages.warning(request,"Username you typed is already exists..Plzzz choose another username or contact admin panel")
            return redirect("register_patient")

        user = User.objects.create_user(username=uname, password=passwd2)
        user.is_active = True  # Enable login
        user.save()
        Patient.objects.create(user=user, 
                                first_name=fname, 
                                last_name=lname,
                                username=uname,
                                mobile_number = mobile,
                                passwd = passwd1,
                                age=age)
        messages.success(request, "Your registration is successfull..plz login with username and password")
        return redirect('patient_login')
    
    return render(request, 'register_patient.html')

def patient_login(request):
    if request.method=="POST":
        uname = request.POST['uname']
        passwd = request.POST['passwd']
        user = authenticate(username=uname,password=passwd)
        if user is not None: # User validation
            login(request,user)
            patient_obj = Patient.objects.get(username=uname)

            # Store patient details in session
            request.session['patient_id'] = patient_obj.patient_id
            request.session['patient_name'] = patient_obj.first_name
            request.session['is_logged_in'] = True 
            data ={
                'patient_obj':patient_obj
            } 
            messages.success(request,"Logged in successfully...")
            return redirect("patient_dashboard")
        else:
            messages.error(request,"Invalid login Credential")
            return redirect("patient_login")
    return render(request,'patient_login.html')

def patient_dashboard(request):
    patient_id = request.session.get('patient_id')

    if patient_id:
        # Retrieve the patient object
        patient_obj = Patient.objects.get(patient_id=patient_id)
        
        # Retrieve all doctors for the dropdown list
        doctors = Doctor.objects.all()
        data = {
            "patient_obj": patient_obj,
            "doctors": doctors,
        }
        return render(request, "patient_dashboard.html", context=data)
    else:
        messages.warning(request,'Patient is not logged in.....')
        return redirect("patient_login")

def patient_appointments(request):
    if request.user.is_authenticated:
        patient = request.user.patient
        appt_obj = Appointment.objects.filter(patient=patient).order_by('appointment_date') # Ascending
            
        context = {
            'appt_obj':appt_obj,
            'patient':patient
        }

        return render(request,"patient_appointments.html",context)
    else:
       messages.warning(request, "Session expired...Please login")
       return redirect('patient_login')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')  # Redirect to the home page or any other page

######################### Book Appointment #################################################

def book_appointment(request):
    if request.user.is_authenticated:
        doctors_with_availability = Doctor.objects.annotate(
                has_availability=Exists(
                    DoctorAvailability.objects.filter(
                        doctor=OuterRef('pk'),
                        available_date__gte=date.today()
                    )
                )
            ).filter(has_availability=True, approval=True)  # Only approved doctors    selected_doctor = None
        
        available_dates = []
        selected_doctor = None
        services = Service.objects.all()

        if request.method == 'POST':
            patient_id = request.session.get('patient_id')
            patient_obj = Patient.objects.get(patient_id=patient_id)
            current_doctor_id = request.POST.get('doctor_id') #
            appointment_date_str = request.POST.get('appointment_date', "")
            selected_services = request.POST.getlist('services')  # Get the selected services
        
            # Check if doctor_id is different from previously selected doctor
            previous_doctor_id = request.session.get('previous_doctor_id') # ""
            if current_doctor_id and current_doctor_id != previous_doctor_id: 
                appointment_date_str = ""
                request.session['previous_doctor_id'] = current_doctor_id

            if current_doctor_id:
                selected_doctor = Doctor.objects.get(doctor_id=current_doctor_id)
                available_dates = DoctorAvailability.objects.filter(
                    doctor=selected_doctor, 
                    available_date__gte=date.today()
                ).values_list('available_date', flat=True)

                # Save appointment when the date is selected
                if appointment_date_str:
                    try:
                        appointment_date = datetime.strptime(appointment_date_str, "%b. %d, %Y")

                        # Check for existing appointments
                        existing_appointment = Appointment.objects.filter(patient=patient_obj, 
                                                    doctor=selected_doctor, 
                                                    appointment_date=appointment_date).exists()
                        if existing_appointment:
                            messages.warning(request, "You already have an appointment with this doctor on this date.")
                            return redirect('book_appointment')
                        
                        # Create a new appointment
                        appointment = Appointment(
                            patient=patient_obj,  # Assuming you have a Patient model linked to User
                            doctor=selected_doctor,
                            appointment_date=appointment_date
            
                        )
                        appointment.save()

                        # Add selected services to the appointment
                        for service_id in selected_services:
                            service = Service.objects.get(id=service_id)
                            appointment.services.add(service)
                        messages.success(request,"Appointment created successfully...")
                        return redirect('patient_dashboard')
                    except ValueError:
                        messages.error(request, "Invalid date format selected.")
                        return redirect('patient_dashboard')
            else:
                messages.warning(request,"No doctor")

        context = {
            'approved_doctors': doctors_with_availability, # approved_doctors_availability
            'selected_doctor': selected_doctor,
            'available_dates': available_dates,
            'services': services,
        }
        return render(request, 'book_appointment.html', context)
    else:
        # If the user is not authenticated, redirect to the login page or show a message
        messages.warning(request, "Session expired...Please login")
        return redirect('patient_login')  

def appt_approve(request,appt_id):
    if request.user.is_authenticated:
        appt = Appointment.objects.get(appt_id=appt_id)
        appt.appt_status = "completed"
        appt.save()
        messages.success(request, "Appointment status updated successfully")
        return redirect('doctor_appointments')  
    else:
        messages.warning(request, "Session expired...Please login")
        return redirect('patient_login')
    
def appt_reject(request,appt_id):
    if request.user.is_authenticated:
        appt = Appointment.objects.get(appt_id=appt_id)
        appt.appt_status = "rejected"
        appt.save()
        messages.success(request, "Appointment status updated successfully")
        return redirect('doctor_appointments')  
    else:
        messages.warning(request, "Session expired...Please login")
        return redirect('patient_login')







