from django.contrib import admin
from django.urls import path
from appointments import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
]