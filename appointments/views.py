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


@login_required
def admin_dashboard(request):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    return render(request, 'appointments/admin_dashboard.html')


@login_required
def customer_dashboard(request):
    if request.user.profile.role != 'customer':
        return redirect('admin_dashboard')
    return render(request, 'appointments/customer_dashboard.html')

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

@login_required
def manage_appointments(request):
    if request.user.profile.role != 'admin':
        return redirect('customer_dashboard')
    appointments = Appointment.objects.select_related('customer', 'service').all()
    return render(request, 'appointments/manage_appointments.html', {'appointments': appointments})