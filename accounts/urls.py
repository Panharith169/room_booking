from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('profile/', views.user_profile_view, name='user_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Dashboard and role-based views
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('manage-rooms/', views.manage_rooms_view, name='manage_rooms'),
    path('all-bookings/', views.all_bookings_view, name='all_bookings'),
]