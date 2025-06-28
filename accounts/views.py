from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .forms import CustomUserRegistrationForm, CustomLoginForm, UserProfileForm

class UserRegistrationView(CreateView):
    """Class-based view for user registration"""
    form_class = CustomUserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! You can now log in.')
        return response
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


def custom_login_view(request):
    """Custom login view using email"""
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.get_user().username
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                next_page = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_page)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})


def custom_logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')


@login_required
def user_profile_view(request):
    """User profile view and edit functionality"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:user_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'registration/profile.html', context)


@login_required
def change_password_view(request):
    """Password change functionality"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:user_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'registration/change_password.html', {'form': form})


# ============================================================================
# USER PERMISSIONS AND AUTHORIZATION
# ============================================================================

def setup_user_groups():
    """Set up user groups and permissions (run this in management command or shell)"""
    
    # Create groups
    admin_group, created = Group.objects.get_or_create(name='Administrators')
    staff_group, created = Group.objects.get_or_create(name='Staff')
    regular_group, created = Group.objects.get_or_create(name='Regular Users')
    
    # Get or create custom permissions
    content_type = ContentType.objects.get_for_model(User)
    
    # Custom permissions
    permissions = [
        ('can_manage_rooms', 'Can manage rooms'),
        ('can_view_all_bookings', 'Can view all bookings'),
        ('can_manage_users', 'Can manage users'),
        ('can_generate_reports', 'Can generate reports'),
    ]
    
    for codename, name in permissions:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )
    
    # Assign permissions to groups
    admin_permissions = Permission.objects.filter(
        codename__in=['can_manage_rooms', 'can_view_all_bookings', 
                     'can_manage_users', 'can_generate_reports']
    )
    staff_permissions = Permission.objects.filter(
        codename__in=['can_manage_rooms', 'can_view_all_bookings']
    )
    
    admin_group.permissions.set(admin_permissions)
    staff_group.permissions.set(staff_permissions)


def assign_user_role(user, role):
    """Assign role to user"""
    # Remove user from all groups first
    user.groups.clear()
    
    try:
        group = Group.objects.get(name=role)
        user.groups.add(group)
        
        # Set staff status for admins and staff
        if role in ['Administrators', 'Staff']:
            user.is_staff = True
        else:
            user.is_staff = False
            
        # Set superuser status for admins only
        if role == 'Administrators':
            user.is_superuser = True
        else:
            user.is_superuser = False
            
        user.save()
        return True
    except Group.DoesNotExist:
        return False


def get_user_role(user):
    """Get user's primary role"""
    if user.groups.filter(name='Administrators').exists():
        return 'Administrator'
    elif user.groups.filter(name='Staff').exists():
        return 'Staff'
    elif user.groups.filter(name='Regular Users').exists():
        return 'Regular User'
    else:
        return 'No Role Assigned'


# Permission Decorators
def admin_required(view_func):
    """Decorator to require admin role"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not request.user.groups.filter(name='Administrators').exists():
            messages.error(request, 'Administrator access required.')
            raise PermissionDenied("Administrator access required.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def staff_required(view_func):
    """Decorator to require staff role or higher"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not (request.user.groups.filter(name='Administrators').exists() or 
                request.user.groups.filter(name='Staff').exists()):
            messages.error(request, 'Staff access required.')
            raise PermissionDenied("Staff access required.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def permission_required_custom(permission_codename):
    """Custom permission decorator"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if not request.user.has_perm(f'auth.{permission_codename}'):
                messages.error(request, 'You do not have permission to access this page.')
                raise PermissionDenied("Insufficient permissions.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Example protected views
@admin_required
def admin_dashboard_view(request):
    """Admin-only dashboard"""
    context = {
        'total_users': User.objects.count(),
        'admin_count': User.objects.filter(groups__name='Administrators').count(),
        'staff_count': User.objects.filter(groups__name='Staff').count(),
        'regular_count': User.objects.filter(groups__name='Regular Users').count(),
    }
    return render(request, 'admin/dashboard.html', context)


@staff_required
def manage_rooms_view(request):
    """Staff and admin access to room management"""
    return render(request, 'rooms/manage.html')


@permission_required_custom('can_view_all_bookings')
def all_bookings_view(request):
    """View requiring specific permission"""
    return render(request, 'bookings/all_bookings.html')


@login_required
def dashboard_view(request):
    """General dashboard with role-based content"""
    user_role = get_user_role(request.user)
    
    context = {
        'user_role': user_role,
        'can_manage_rooms': request.user.has_perm('auth.can_manage_rooms'),
        'can_view_all_bookings': request.user.has_perm('auth.can_view_all_bookings'),
        'can_manage_users': request.user.has_perm('auth.can_manage_users'),
        'can_generate_reports': request.user.has_perm('auth.can_generate_reports'),
    }
    return render(request, 'dashboard.html', context)