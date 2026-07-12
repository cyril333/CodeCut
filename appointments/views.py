from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistrationForm
from .models import Profile


def auth_view(request):
    login_form_errors = None
    register_form = RegistrationForm()

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            username = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                profile = Profile.objects.get(user=user)
                if profile.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('customer_dashboard')
            else:
                login_form_errors = "Invalid email or password."

        elif 'register_submit' in request.POST:
            register_form = RegistrationForm(request.POST)
            if register_form.is_valid():
                data = register_form.cleaned_data
                user = User.objects.create_user(
                    username=data['email'],
                    email=data['email'],
                    password=data['password'],
                )
                Profile.objects.create(
                    user=user,
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    role='customer'
                )
                messages.success(request, "Account created successfully. Please log in.")
                return redirect('auth')

    context = {
        'register_form': register_form,
        'login_form_errors': login_form_errors,
    }
    return render(request, 'appointments/auth.html', context)


def logout_view(request):
    logout(request)
    return redirect('auth')

from django.contrib.auth.decorators import login_required


from django.utils import timezone

@login_required
def admin_dashboard(request):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')

    pending_count = Appointment.objects.filter(status='pending').count()
    confirmed_today_count = Appointment.objects.filter(status='confirmed', appointment_date=timezone.localdate()).count()
    total_customers_count = Profile.objects.filter(role='customer').count()

    context = {
        'pending_count': pending_count,
        'confirmed_today_count': confirmed_today_count,
        'total_customers_count': total_customers_count,
    }
    return render(request, 'appointments/admin_dashboard.html', context)


from django.db.models import Case, When, Value, IntegerField

@login_required
def customer_dashboard(request):
    if request.user.profile.role != 'customer':
        return redirect('admin_dashboard')
    appointments = Appointment.objects.filter(customer=request.user).annotate(
        status_order=Case(
            When(status='confirmed', then=Value(0)),
            When(status='pending', then=Value(1)),
            When(status='cancelled', then=Value(2)),
            output_field=IntegerField()
        ),
        pay_order=Case(
            When(pay_status='paid', then=Value(0)),
            When(pay_status='unpaid', then=Value(1)),
            output_field=IntegerField()
        )
    ).order_by('status_order', 'pay_order', '-appointment_date')
    return render(request, 'appointments/customer_dashboard.html', {'appointments': appointments})

from .models import Service
from .forms import ServiceForm

@login_required
def manage_services(request):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service added successfully.")
            return redirect('manage_services')
    else:
        form = ServiceForm()

    services = Service.objects.all()
    return render(request, 'appointments/manage_services.html', {'form': form, 'services': services})

from django.shortcuts import get_object_or_404

@login_required
def delete_service(request, service_id):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    messages.success(request, "Service deleted successfully.")
    return redirect('manage_services')


@login_required
def toggle_service_status(request, service_id):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    service = get_object_or_404(Service, id=service_id)
    service.status = 'inactive' if service.status == 'active' else 'active'
    service.save()
    return redirect('manage_services')

from .models import Appointment

from django.db.models import Case, When, Value, IntegerField

@login_required
def manage_appointments(request):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    appointments = Appointment.objects.select_related('customer', 'service').annotate(
        status_order=Case(
            When(status='confirmed', then=Value(0)),
            When(status='pending', then=Value(1)),
            When(status='cancelled', then=Value(2)),
            output_field=IntegerField()
        )
    ).order_by('status_order', '-appointment_date')
    return render(request, 'appointments/manage_appointments.html', {'appointments': appointments})

from .forms import AppointmentForm

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user

            conflict = Appointment.objects.filter(
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time,
                status__in=['pending', 'confirmed']
            ).exists()

            if conflict:
                messages.error(request, "That time slot is already booked. Please choose another.")
            else:
                appointment.save()
                messages.success(request, "Appointment booked successfully.")
                return redirect('customer_dashboard')
    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
def confirm_appointment(request, appointment_id):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'confirmed'
    appointment.save()
    messages.success(request, "Appointment confirmed.")
    return redirect('manage_appointments')


@login_required
def cancel_appointment(request, appointment_id):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'cancelled'
    appointment.save()
    messages.success(request, "Appointment cancelled.")
    return redirect('manage_appointments')

from .forms import ProfileForm

@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'appointments/profile.html', {'form': form, 'profile': profile})

@login_required
def manage_customers(request):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    customers = Profile.objects.filter(role='customer').select_related('user')
    return render(request, 'appointments/manage_customers.html', {'customers': customers})

@login_required
def toggle_pay_status(request, appointment_id):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.pay_status = 'unpaid' if appointment.pay_status == 'paid' else 'paid'
    appointment.save()
    return redirect('manage_appointments')

from django.http import JsonResponse

@login_required
def get_booked_slots(request):
    date = request.GET.get('date')
    booked = Appointment.objects.filter(
        appointment_date=date,
        status__in=['pending', 'confirmed']
    ).values_list('appointment_time', flat=True)
    booked_times = [t.strftime('%H:%M') for t in booked]
    return JsonResponse({'booked': booked_times})

@login_required
def delete_customer(request, profile_id):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    profile = get_object_or_404(Profile, id=profile_id)
    profile.user.delete()
    messages.success(request, "Customer deleted.")
    return redirect('manage_customers')