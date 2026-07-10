from django.contrib import admin
from django.urls import path
from appointments import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/admin/services/', views.manage_services, name='manage_services'),
    path('dashboard/admin/services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('dashboard/admin/services/toggle/<int:service_id>/', views.toggle_service_status, name='toggle_service_status'),
    path('dashboard/admin/appointments/', views.manage_appointments, name='manage_appointments'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('dashboard/admin/appointments/confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('dashboard/admin/appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
]