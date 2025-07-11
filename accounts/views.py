from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from functools import wraps

# Get the custom User model
User = get_user_model()

# ============================================================================
# ACCESS CONTROL DECORATORS AND MIDDLEWARE
# ============================================================================

def admin_required(view_func):
    """Decorator to ensure only admins can access admin views"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        user_role = get_user_role(request.user)
        if user_role != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('accounts:user_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def user_required(view_func):
    """Decorator to ensure only regular users can access user views"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        user_role = get_user_role(request.user)
        if user_role == 'Admin':
            messages.info(request, 'Redirecting to admin dashboard.')
            return redirect('accounts:admin_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def role_redirect(view_func):
    """Decorator to redirect based on user role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        user_role = get_user_role(request.user)
        if user_role == 'Admin':
            return redirect('accounts:admin_dashboard')
        else:
            return redirect('accounts:user_dashboard')
    return wrapper

# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

# filepath: c:\Users\User\Desktop\Year2\Project_S2\RoomBooking\accounts\views.py
# Just update the registration view to work with your HTML:

def register(request):
    """User registration view - Works with your existing HTML"""
    if request.method == 'POST':
        try:
            # Get form data exactly as your HTML sends it
            first_name = request.POST.get('firstName', '').strip()
            last_name = request.POST.get('lastName', '').strip()
            email = request.POST.get('email', '').strip()
            faculty = request.POST.get('faculty', '').strip()
            department = request.POST.get('department', '').strip()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirmPassword', '')
            student_id = request.POST.get('studentId', '').strip()
            phone_number = request.POST.get('phoneNumber', '').strip()
            
            # Basic validation
            if not all([first_name, last_name, email, password, confirm_password]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'SignIn-RegisterPage/register.html')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'SignIn-RegisterPage/register.html')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'SignIn-RegisterPage/register.html')
            
            # Create user with flexible fields
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                student_id=student_id or f"USR{User.objects.count() + 1:06d}",
                phone_number=phone_number or "000-000-0000",
                faculty=faculty,
                department=department
            )
            
            # Setup user role
            from django.contrib.auth.models import Group
            user_group, created = Group.objects.get_or_create(name='User')
            user.groups.add(user_group)
            
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('accounts:login')
            
        except Exception as e:
            print(f"Registration error: {e}")
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'SignIn-RegisterPage/register.html')
    
    return render(request, 'SignIn-RegisterPage/register.html')

def custom_login_view(request):
    """Login view - Routes to appropriate dashboard based on account type"""
    if request.method == 'POST':
        email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        print(f"Login attempt for: {email}")
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            
            user_role = get_user_role(user)
            print(f"User: {user.email}, Role: {user_role}")
            
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Role-based redirect
            if user_role == 'Admin':
                print("Admin login - redirecting to admin dashboard")
                return redirect('accounts:admin_dashboard')
            else:
                print("User login - redirecting to user dashboard")
                return redirect('accounts:user_dashboard')
        else:
            print("Authentication failed")
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'SignIn-RegisterPage/login.html')

def custom_logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

# ============================================================================
# USER VIEWS (All UserPage Templates) - FOR STUDENTS
# ============================================================================

@login_required
@user_required
def user_dashboard_view(request):
    """User dashboard - UserPage/featureRoom.html"""
    user_role = get_user_role(request.user)
    
    # Get real room data from database
    try:
        from booking.models import Room
        rooms = Room.objects.filter(is_available=True).order_by('room_number')
        
        # Convert rooms to format expected by frontend
        rooms_data = []
        for room in rooms:
            # Build location string
            location = room.room_number
            if room.room_number.startswith('A-'):
                location = f"Building A, {room.room_number}"
            elif room.room_number.startswith('S-'):
                location = f"Building STEM, {room.room_number}"
            elif room.room_number.startswith('L-'):
                location = f"Library Building, {room.room_number}"
            elif room.room_number.startswith('B-'):
                location = f"Business Building, {room.room_number}"
            elif room.room_number.startswith('G'):
                location = f"Main Building, {room.room_number}"
            elif room.room_number.startswith('C'):
                location = f"Science Building, {room.room_number}"
            
            # Parse features from equipment field
            features = []
            if room.equipment:
                features = [feature.strip() for feature in room.equipment.split(',') if feature.strip()]
            
            rooms_data.append({
                'id': room.id,
                'name': room.name,
                'location': location,
                'capacity': room.capacity,
                'type': room.room_type,
                'features': features,
                'available': room.is_available and room.availability_status == 'available',
                'description': room.description or f"Modern {room.get_room_type_display().lower()} with capacity for {room.capacity} people.",
                'image_url': room.image.url if room.image else '/static/images/default-room.jpg',
                'room_number': room.room_number,
            })
        
    except ImportError:
        # Fallback if booking models don't exist
        rooms_data = []
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'rooms_data': rooms_data,  # Add real room data
    }
    
    return render(request, 'UserPage/featureRoom.html', context)

@login_required
@user_required
def booking_view(request):
    """Room booking - UserPage/booking.html - Integration with booking app"""
    user_role = get_user_role(request.user)
    
    # Get URL parameters for autofill
    room_id = request.GET.get('room_id')
    date_param = request.GET.get('date')
    time_param = request.GET.get('time')
    
    # Import booking models
    try:
        from booking.models import Room, Booking
        
        # Get available rooms for the form
        rooms = Room.objects.filter(is_available=True).order_by('room_number')
        
        # Get selected room details if room_id is provided
        selected_room = None
        if room_id:
            try:
                selected_room = Room.objects.get(id=room_id, is_available=True)
            except Room.DoesNotExist:
                selected_room = None
        
        # Get today's date for form minimum date
        today = timezone.now().date()
        
        # Get user's booking statistics
        user_bookings = Booking.objects.filter(user=request.user)
        total_bookings = user_bookings.count()
        pending_bookings = user_bookings.filter(status='pending').count()
        confirmed_bookings = user_bookings.filter(status='confirmed').count()
        
        # Get recent bookings for reference
        recent_bookings = user_bookings.order_by('-created_at')[:5]
        
        # Get buildings if available
        try:
            from booking.models import Building
            buildings = Building.objects.all()
        except:
            # Create default buildings if model doesn't exist
            buildings = [
                {'id': 1, 'name': 'Building A', 'code': 'A'},
                {'id': 2, 'name': 'Building STEM', 'code': 'S'},
                {'id': 3, 'name': 'Library Building', 'code': 'L'},
                {'id': 4, 'name': 'Business Building', 'code': 'B'},
            ]
        
        # Get room types for filtering
        room_types = Room.ROOM_TYPES
        
        # Check if user has reached daily booking limit
        daily_bookings = user_bookings.filter(
            start_time__date=today,
            status__in=['confirmed', 'pending']
        ).count()
        
        can_book_today = daily_bookings < 3  # Maximum 3 bookings per day
        
        context = {
            'user': request.user,
            'user_role': user_role,
            'rooms': rooms,
            'buildings': buildings,
            'room_types': room_types,
            'today': today,
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'recent_bookings': recent_bookings,
            'can_book_today': can_book_today,
            'daily_bookings': daily_bookings,
            'max_daily_bookings': 3,
            # Autofill parameters
            'selected_room': selected_room,
            'autofill_room_id': room_id,
            'autofill_date': date_param,
            'autofill_time': time_param,
        }
        
    except ImportError:
        # Fallback if booking models don't exist
        rooms = [
            {'id': 1, 'name': 'Room 101', 'room_number': 'A-101', 'capacity': 30, 'room_type': 'classroom'},
            {'id': 2, 'name': 'Room 102', 'room_number': 'A-102', 'capacity': 25, 'room_type': 'classroom'},
            {'id': 3, 'name': 'Room 201', 'room_number': 'B-201', 'capacity': 50, 'room_type': 'conference'},
            {'id': 4, 'name': 'Computer Lab 1', 'room_number': 'S-206', 'capacity': 30, 'room_type': 'lab'},
            {'id': 5, 'name': 'Study Room 1', 'room_number': 'L-105', 'capacity': 8, 'room_type': 'study'},
        ]
        
        buildings = [
            {'id': 1, 'name': 'Building A', 'code': 'A'},
            {'id': 2, 'name': 'Building STEM', 'code': 'S'},
            {'id': 3, 'name': 'Library Building', 'code': 'L'},
            {'id': 4, 'name': 'Business Building', 'code': 'B'},
        ]
        
        room_types = [
            ('classroom', 'Classroom'),
            ('lab', 'Laboratory'),
            ('conference', 'Conference Room'),
            ('study', 'Study Room'),
        ]
        
        context = {
            'user': request.user,
            'user_role': user_role,
            'rooms': rooms,
            'buildings': buildings,
            'room_types': room_types,
            'today': timezone.now().date(),
            'total_bookings': 0,
            'pending_bookings': 0,
            'confirmed_bookings': 0,
            'recent_bookings': [],
            'can_book_today': True,
            'daily_bookings': 0,
            'max_daily_bookings': 3,
        }
    
    return render(request, 'UserPage/booking.html', context)

@login_required
@user_required
def booked_view(request):
    """User's bookings - UserPage/booked.html"""
    user_role = get_user_role(request.user)
    
    # Get user's bookings
    try:
        from booking.models import Booking
        
        # Get all bookings for the user
        bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
        
        # Separate bookings by status
        pending_bookings = bookings.filter(status='pending')
        confirmed_bookings = bookings.filter(status='confirmed')
        cancelled_bookings = bookings.filter(status='cancelled')
        completed_bookings = bookings.filter(status='completed')
        
        # Get upcoming bookings (confirmed and pending)
        upcoming_bookings = bookings.filter(
            start_time__gt=timezone.now(),
            status__in=['confirmed', 'pending']
        ).order_by('start_time')
        
        # Get past bookings
        past_bookings = bookings.filter(
            end_time__lt=timezone.now()
        ).order_by('-start_time')
        
        # Get today's bookings
        today = timezone.now().date()
        today_bookings = bookings.filter(
            start_time__date=today,
            status__in=['confirmed', 'pending']
        ).order_by('start_time')
        
        # Calculate statistics
        total_bookings = bookings.count()
        pending_count = pending_bookings.count()
        confirmed_count = confirmed_bookings.count()
        cancelled_count = cancelled_bookings.count()
        completed_count = completed_bookings.count()
        
        # Get booking history for the last 30 days
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_bookings = bookings.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')
        
        # Add cancellation information
        for booking in bookings:
            booking.can_cancel = booking.can_cancel() if hasattr(booking, 'can_cancel') else (
                booking.status in ['pending', 'confirmed'] and 
                booking.start_time > timezone.now()
            )
            booking.can_modify = booking.can_be_modified() if hasattr(booking, 'can_be_modified') else (
                booking.status == 'pending' and 
                booking.start_time > timezone.now()
            )
        
        # Handle booking actions
        if request.method == 'POST':
            action = request.POST.get('action')
            booking_id = request.POST.get('booking_id')
            
            if action and booking_id:
                try:
                    booking = Booking.objects.get(id=booking_id, user=request.user)
                    
                    if action == 'cancel':
                        if booking.can_cancel:
                            booking.status = 'cancelled'
                            booking.save()
                            messages.success(request, f'Booking for {booking.room.name} has been cancelled.')
                        else:
                            messages.error(request, 'This booking cannot be cancelled.')
                    
                    elif action == 'request_modification':
                        if booking.can_modify:
                            messages.info(request, 'Modification request submitted. Please contact admin for changes.')
                        else:
                            messages.error(request, 'This booking cannot be modified.')
                    
                    return redirect('accounts:booked')
                    
                except Booking.DoesNotExist:
                    messages.error(request, 'Booking not found.')
        
        context = {
            'user': request.user,
            'user_role': user_role,
            'bookings': bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'completed_bookings': completed_bookings,
            'upcoming_bookings': upcoming_bookings,
            'past_bookings': past_bookings,
            'today_bookings': today_bookings,
            'recent_bookings': recent_bookings,
            'total_bookings': total_bookings,
            'pending_count': pending_count,
            'confirmed_count': confirmed_count,
            'cancelled_count': cancelled_count,
            'completed_count': completed_count,
        }
        
    except ImportError:
        # Fallback if booking models don't exist
        context = {
            'user': request.user,
            'user_role': user_role,
            'bookings': [],
            'pending_bookings': [],
            'confirmed_bookings': [],
            'cancelled_bookings': [],
            'completed_bookings': [],
            'upcoming_bookings': [],
            'past_bookings': [],
            'today_bookings': [],
            'recent_bookings': [],
            'total_bookings': 0,
            'pending_count': 0,
            'confirmed_count': 0,
            'cancelled_count': 0,
            'completed_count': 0,
        }
    
    return render(request, 'UserPage/booked.html', context)

@login_required
@user_required
def view_rooms_view(request):
    """View rooms - UserPage/rooms.html (For regular users only)"""
    user_role = get_user_role(request.user)
    
    # Get available rooms for users
    try:
        from booking.models import Room
        rooms = Room.objects.filter(is_available=True).order_by('room_number')
    except ImportError:
        # Fallback if booking models don't exist
        rooms = [
            {'id': 1, 'name': 'Conference Room A', 'room_number': 'A-201', 'capacity': 20, 'room_type': 'conference', 'description': 'Modern conference room', 'equipment': 'Projector, Whiteboard'},
            {'id': 2, 'name': 'Computer Lab 1', 'room_number': 'A-206', 'capacity': 30, 'room_type': 'lab', 'description': 'Fully equipped computer lab', 'equipment': '30 PCs, Projector'},
            {'id': 3, 'name': 'Lecture Hall', 'room_number': 'A-101', 'capacity': 100, 'room_type': 'classroom', 'description': 'Large lecture hall', 'equipment': 'Audio system, Projector'},
            {'id': 4, 'name': 'Study Room 1', 'room_number': 'B-105', 'capacity': 8, 'room_type': 'study', 'description': 'Quiet study room', 'equipment': 'Whiteboard, Tables'},
            {'id': 5, 'name': 'Chemistry Lab', 'room_number': 'S-309', 'capacity': 25, 'room_type': 'lab', 'description': 'Chemistry laboratory', 'equipment': 'Lab equipment, Safety gear'},
        ]
    except Exception as e:
        messages.error(request, f'Error loading rooms: {str(e)}')
        rooms = []
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'rooms': rooms,
        'today': timezone.now().date(),
    }
    
    return render(request, 'UserPage/rooms.html', context)

@login_required
@admin_required
def admin_view_rooms_view(request):
    """View all rooms - AdminPage/viewRooms.html (For admins only)"""
    user_role = get_user_role(request.user)
    
    # Get all rooms for admin
    try:
        from booking.models import Room
        rooms = Room.objects.all().order_by('room_number')
        
        # Get room statistics
        total_rooms = rooms.count()
        available_rooms = rooms.filter(is_available=True).count()
        unavailable_rooms = rooms.filter(is_available=False).count()
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            rooms = rooms.filter(
                Q(name__icontains=search_query) |
                Q(room_number__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by room type
        room_type = request.GET.get('room_type', '')
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        
        # Filter by availability
        availability = request.GET.get('availability', '')
        if availability:
            rooms = rooms.filter(is_available=(availability == 'true'))
        
        # Get room types for filter dropdown
        room_types = Room.ROOM_TYPES
        
        # Group rooms by type
        room_types_dict = {}
        for room in rooms:
            room_type = room.room_type
            if room_type not in room_types_dict:
                room_types_dict[room_type] = []
            room_types_dict[room_type].append(room)
        
    except ImportError:
        # Fallback if booking models don't exist
        rooms = [
            {'id': 1, 'name': 'Conference Room A', 'room_number': 'A-201', 'capacity': 20, 'room_type': 'conference', 'is_available': True, 'description': 'Modern conference room', 'equipment': 'Projector, Whiteboard'},
            {'id': 2, 'name': 'Computer Lab 1', 'room_number': 'A-206', 'capacity': 30, 'room_type': 'lab', 'is_available': True, 'description': 'Fully equipped computer lab', 'equipment': '30 PCs, Projector'},
            {'id': 3, 'name': 'Lecture Hall', 'room_number': 'A-101', 'capacity': 100, 'room_type': 'classroom', 'is_available': False, 'description': 'Large lecture hall', 'equipment': 'Audio system, Projector'},
            {'id': 4, 'name': 'Chemistry Lab', 'room_number': 'S-309', 'capacity': 25, 'room_type': 'lab', 'is_available': True, 'description': 'Chemistry laboratory', 'equipment': 'Lab equipment, Safety gear'},
            {'id': 5, 'name': 'Study Room 1', 'room_number': 'B-105', 'capacity': 8, 'room_type': 'study', 'is_available': True, 'description': 'Quiet study room', 'equipment': 'Whiteboard, Tables'},
            {'id': 6, 'name': 'Meeting Room B', 'room_number': 'B-202', 'capacity': 15, 'room_type': 'conference', 'is_available': False, 'description': 'Small meeting room', 'equipment': 'TV, Conference phone'},
        ]
        total_rooms = len(rooms)
        available_rooms = sum(1 for room in rooms if room.get('is_available', True))
        unavailable_rooms = total_rooms - available_rooms
        
        # Group fallback rooms by type
        room_types_dict = {}
        for room in rooms:
            room_type = room['room_type']
            if room_type not in room_types_dict:
                room_types_dict[room_type] = []
            room_types_dict[room_type].append(room)
        
        room_types = [
            ('classroom', 'Classroom'),
            ('lab', 'Laboratory'),
            ('conference', 'Conference Room'),
            ('auditorium', 'Auditorium'),
            ('library', 'Library Room'),
            ('study', 'Study Room'),
            ('other', 'Other'),
        ]
    except Exception as e:
        messages.error(request, f'Error loading rooms: {str(e)}')
        rooms = []
        total_rooms = 0
        available_rooms = 0
        unavailable_rooms = 0
        room_types_dict = {}
        room_types = []
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'rooms': rooms,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'unavailable_rooms': unavailable_rooms,
        'room_types': room_types_dict,
        'room_types_choices': room_types,
        'search_query': request.GET.get('search', ''),
        'selected_room_type': request.GET.get('room_type', ''),
        'selected_availability': request.GET.get('availability', ''),
    }
    
    return render(request, 'AdminPage/viewRooms.html', context)

@login_required
def create_booking(request):
    """Handle booking creation with comprehensive validation"""
    user_role = get_user_role(request.user)
    
    if user_role == 'Admin':
        return redirect('accounts:admin_dashboard')
    
    if request.method == 'POST':
        try:
            from booking.models import Room, Booking
            from datetime import datetime, date
            from django.utils import timezone
            
            # Get form data
            room_id = request.POST.get('room')
            date_str = request.POST.get('date')
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')
            purpose = request.POST.get('purpose', '').strip()
            attendees = request.POST.get('attendees', 1)
            notes = request.POST.get('notes', '').strip()
            
            # Basic validation
            if not all([room_id, date_str, start_time_str, end_time_str, purpose]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('accounts:booking')
            
            # Parse and validate date and time
            try:
                booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
            except ValueError:
                messages.error(request, 'Invalid date or time format.')
                return redirect('accounts:booking')
            
            # Create timezone-aware datetime objects
            start_datetime = timezone.make_aware(datetime.combine(booking_date, start_time))
            end_datetime = timezone.make_aware(datetime.combine(booking_date, end_time))
            
            # Validate booking is in the future
            if start_datetime <= timezone.now():
                messages.error(request, 'Booking time must be in the future.')
                return redirect('accounts:booking')
            
            # Validate end time is after start time
            if start_datetime >= end_datetime:
                messages.error(request, 'End time must be after start time.')
                return redirect('accounts:booking')
            
            # Validate booking duration (max 8 hours)
            duration = end_datetime - start_datetime
            if duration.total_seconds() > 8 * 3600:
                messages.error(request, 'Maximum booking duration is 8 hours.')
                return redirect('accounts:booking')
            
            # Validate minimum booking duration (30 minutes)
            if duration.total_seconds() < 30 * 60:
                messages.error(request, 'Minimum booking duration is 30 minutes.')
                return redirect('accounts:booking')
            
            # Get room and validate
            try:
                room = Room.objects.get(id=room_id)
            except Room.DoesNotExist:
                messages.error(request, 'Selected room does not exist.')
                return redirect('accounts:booking')
            
            if not room.is_available:
                messages.error(request, 'This room is not available for booking.')
                return redirect('accounts:booking')
            
            # Validate attendees count
            try:
                attendees_count = int(attendees)
                if attendees_count <= 0:
                    messages.error(request, 'Number of attendees must be at least 1.')
                    return redirect('accounts:booking')
                if attendees_count > room.capacity:
                    messages.error(request, f'Number of attendees ({attendees_count}) exceeds room capacity ({room.capacity}).')
                    return redirect('accounts:booking')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid number of attendees.')
                return redirect('accounts:booking')
            
            # Check for conflicts
            conflicts = Booking.objects.filter(
                room=room,
                start_time__lt=end_datetime,
                end_time__gt=start_datetime,
                status__in=['confirmed', 'pending']
            )
            
            if conflicts.exists():
                conflict_booking = conflicts.first()
                conflict_time = conflict_booking.start_time.strftime('%Y-%m-%d %H:%M')
                messages.error(request, f'This time slot conflicts with an existing booking at {conflict_time}.')
                return redirect('accounts:booking')
            
            # Check daily booking limit (optional)
            daily_bookings = Booking.objects.filter(
                user=request.user,
                start_time__date=booking_date,
                status__in=['confirmed', 'pending']
            ).count()
            
            if daily_bookings >= 3:  # Maximum 3 bookings per day
                messages.error(request, 'You have reached the maximum number of bookings per day (3).')
                return redirect('accounts:booking')
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                room=room,
                start_time=start_datetime,
                end_time=end_datetime,
                purpose=purpose,
                attendees=attendees_count,
                additional_notes=notes,
                status='pending'
            )
            
            # Check if this is a redirect from user dashboard
            referrer = request.META.get('HTTP_REFERER', '')
            from_dashboard = ('user-dashboard' in referrer or 
                            'featureRoom' in referrer or 
                            request.GET.get('from_dashboard') == 'true')
            
            # Success message with booking details (only if not from dashboard)
            if not from_dashboard:
                booking_time = start_datetime.strftime('%Y-%m-%d at %H:%M')
                duration_hours = duration.total_seconds() / 3600
                
                messages.success(request, 
                    f'Booking created successfully! '
                    f'Room: {room.name} ({room.room_number}) | '
                    f'Date: {booking_time} | '
                    f'Duration: {duration_hours:.1f} hours | '
                    f'Status: Pending approval'
                )
            
            return redirect('accounts:booked')
            
        except ImportError:
            messages.error(request, 'Booking system is not available.')
            return redirect('accounts:booking')
        except Exception as e:
            messages.error(request, f'Booking failed: {str(e)}')
            return redirect('accounts:booking')
    
    return redirect('accounts:booking')

@login_required
def create_booking_redirect(request):
    """Redirect booking creation to booking app"""
    user_role = get_user_role(request.user)
    
    if user_role == 'Admin':
        return redirect('accounts:admin_dashboard')
    
    # Redirect to booking app's create_booking view
    return redirect('booking:create_booking')

@login_required
@user_required
def setting_view(request):
    """User settings - UserPage/setting.html"""
    user_role = get_user_role(request.user)
    
    context = {
        'user': request.user,
        'user_role': user_role,
    }
    
    return render(request, 'UserPage/setting.html', context)

@login_required
@user_required
def profile_setting_view(request):
    """Edit user profile - UserPage/profileSetting.html"""
    user_role = get_user_role(request.user)
    
    if request.method == 'POST':
        try:
            # Update user profile
            request.user.first_name = request.POST.get('firstName', '')
            request.user.last_name = request.POST.get('lastName', '')
            request.user.faculty = request.POST.get('faculty', '')
            request.user.department = request.POST.get('department', '')
            request.user.phone_number = request.POST.get('phoneNumber', '')
            
            # Handle password change
            current_password = request.POST.get('currentPassword')
            new_password = request.POST.get('newPassword')
            confirm_password = request.POST.get('confirmPassword')
            
            if new_password and confirm_password:
                if current_password and check_password(current_password, request.user.password):
                    if new_password == confirm_password:
                        request.user.set_password(new_password)
                        update_session_auth_hash(request, request.user)
                        messages.success(request, 'Profile and password updated successfully!')
                    else:
                        messages.error(request, 'New passwords do not match.')
                        return render(request, 'UserPage/profileSetting.html', {'user': request.user})
                else:
                    messages.error(request, 'Current password is incorrect.')
                    return render(request, 'UserPage/profileSetting.html', {'user': request.user})
            
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:setting')
            
        except Exception as e:
            messages.error(request, f'Profile update failed: {str(e)}')
    
    context = {
        'user': request.user,
        'user_role': user_role,
    }
    
    return render(request, 'UserPage/profileSetting.html', context)

@login_required
@user_required
def about_us_view(request):
    """About us - UserPage/about-us.html"""
    user_role = get_user_role(request.user)
    
    context = {
        'user': request.user,
        'user_role': user_role,
    }
    
    return render(request, 'UserPage/about-us.html', context)

@login_required
@user_required
def service_view(request):
    """Service/Support - UserPage/service.html"""
    user_role = get_user_role(request.user)
    
    # Handle contact form
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            # Save the contact form or send email
            messages.success(request, 'Your message has been sent successfully!')
            
        except Exception as e:
            messages.error(request, f'Failed to send message: {str(e)}')
    
    context = {
        'user': request.user,
        'user_role': user_role,
    }
    
    return render(request, 'UserPage/service.html', context)

# ============================================================================
# ADMIN VIEWS (All AdminPage Templates) - FOR ADMINS ONLY=====
# ============================================================================

@login_required
@admin_required
def admin_dashboard_view(request):
    """Admin dashboard - AdminPage/adminHomePage.html"""
    user_role = get_user_role(request.user)
    
    # Get admin statistics
    total_users = User.objects.count()
    admin_count = User.objects.filter(groups__name='Admin').count()
    user_count = User.objects.filter(groups__name='User').count()
    
    # Get booking statistics
    try:
        from booking.models import Booking, Room
        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        total_rooms = Room.objects.count()
    except ImportError:
        total_bookings = 0
        pending_bookings = 0
        total_rooms = 0
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'total_users': total_users,
        'admin_count': admin_count,
        'user_count': user_count,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_rooms': total_rooms,
    }
    
    return render(request, 'AdminPage/adminHomePage.html', context)

@login_required
@admin_required
def manage_rooms_view(request):
    """Manage rooms - AdminPage/manageRooms.html"""
    user_role = get_user_role(request.user)
    
    # Handle room management
    if request.method == 'POST':
        try:
            from booking.models import Room
            
            action = request.POST.get('action')
            
            if action == 'add_room':
                # Add room logic
                room_name = request.POST.get('room_name')
                room_number = request.POST.get('room_number')
                room_type = request.POST.get('room_type')
                capacity = request.POST.get('capacity')
                description = request.POST.get('description', '')
                equipment = request.POST.get('equipment', '')
                
                if room_name and room_number and room_type and capacity:
                    # Check if room number already exists
                    if Room.objects.filter(room_number=room_number).exists():
                        messages.error(request, f'Room number "{room_number}" already exists.')
                    else:
                        Room.objects.create(
                            name=room_name,
                            room_number=room_number,
                            room_type=room_type,
                            capacity=int(capacity),
                            description=description,
                            equipment=equipment,
                            is_available=True
                        )
                        messages.success(request, f'Room "{room_name}" added successfully!')
                else:
                    messages.error(request, 'Please fill in all required fields.')
                
            elif action == 'edit_room':
                # Edit room logic
                room_id = request.POST.get('room_id')
                room_name = request.POST.get('room_name')
                room_number = request.POST.get('room_number')
                room_type = request.POST.get('room_type')
                capacity = request.POST.get('capacity')
                description = request.POST.get('description', '')
                equipment = request.POST.get('equipment', '')
                
                if room_id and room_name and room_number and room_type and capacity:
                    try:
                        room = Room.objects.get(id=room_id)
                        
                        # Check if room number already exists (excluding current room)
                        if Room.objects.filter(room_number=room_number).exclude(id=room_id).exists():
                            messages.error(request, f'Room number "{room_number}" already exists.')
                        else:
                            room.name = room_name
                            room.room_number = room_number
                            room.room_type = room_type
                            room.capacity = int(capacity)
                            room.description = description
                            room.equipment = equipment
                            room.save()
                            messages.success(request, f'Room "{room_name}" updated successfully!')
                    except Room.DoesNotExist:
                        messages.error(request, 'Room not found.')
                    except ValueError:
                        messages.error(request, 'Invalid capacity value. Please enter a number.')
                else:
                    messages.error(request, 'Please fill in all required fields.')
                
            elif action == 'delete_room':
                # Delete room logic
                room_id = request.POST.get('room_id')
                if room_id:
                    try:
                        room = Room.objects.get(id=room_id)
                        room_name = room.name
                        
                        # Check if room has active bookings
                        active_bookings = room.bookings.filter(
                            status__in=['confirmed', 'pending'],
                            start_time__gte=timezone.now()
                        )
                        
                        if active_bookings.exists():
                            messages.error(request, f'Cannot delete room "{room_name}". It has active bookings.')
                        else:
                            room.delete()
                            messages.success(request, f'Room "{room_name}" deleted successfully!')
                    except Room.DoesNotExist:
                        messages.error(request, 'Room not found.')
                        
            elif action == 'toggle_availability':
                # Toggle room availability
                room_id = request.POST.get('room_id')
                if room_id:
                    try:
                        room = Room.objects.get(id=room_id)
                        room.is_available = not room.is_available
                        room.save()
                        status = 'available' if room.is_available else 'unavailable'
                        messages.success(request, f'Room "{room.name}" is now {status}!')
                    except Room.DoesNotExist:
                        messages.error(request, 'Room not found.')
                        
        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}')
        except Exception as e:
            messages.error(request, f'Room management failed: {str(e)}')
    
    # Get rooms data
    try:
        from booking.models import Room
        rooms = Room.objects.all().order_by('room_number')
        
        # Get room types for the form
        room_types = Room.ROOM_TYPES
        
        # Get room statistics
        total_rooms = rooms.count()
        available_rooms = rooms.filter(is_available=True).count()
        unavailable_rooms = rooms.filter(is_available=False).count()
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            rooms = rooms.filter(
                Q(name__icontains=search_query) |
                Q(room_number__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by room type
        room_type_filter = request.GET.get('room_type', '')
        if room_type_filter:
            rooms = rooms.filter(room_type=room_type_filter)
        
        # Filter by availability
        availability_filter = request.GET.get('availability', '')
        if availability_filter:
            rooms = rooms.filter(is_available=(availability_filter == 'true'))
        
    except ImportError:
        rooms = []
        room_types = [
            ('classroom', 'Classroom'),
            ('lab', 'Laboratory'),
            ('conference', 'Conference Room'),
            ('auditorium', 'Auditorium'),
            ('library', 'Library Room'),
            ('study', 'Study Room'),
            ('other', 'Other'),
        ]
        total_rooms = 0
        available_rooms = 0
        unavailable_rooms = 0
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'rooms': rooms,
        'room_types': room_types,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'unavailable_rooms': unavailable_rooms,
        'search_query': request.GET.get('search', ''),
        'selected_room_type': request.GET.get('room_type', ''),
        'selected_availability': request.GET.get('availability', ''),
    }
    
    return render(request, 'AdminPage/admin_room_management.html', context)

@login_required
@admin_required
def all_bookings_view(request):
    """All bookings - AdminPage/allBookings.html"""
    user_role = get_user_role(request.user)
    
    # Handle booking actions
    if request.method == 'POST':
        try:
            from booking.models import Booking
            
            action = request.POST.get('action')
            booking_id = request.POST.get('booking_id')
            
            if action and booking_id:
                booking = Booking.objects.get(id=booking_id)
                
                if action == 'approve':
                    booking.status = 'confirmed'  # Use 'confirmed' to match the model
                    booking.save()
                    messages.success(request, f'Booking for {booking.room.name} has been approved!')
                    
                elif action == 'reject' or action == 'deny':
                    booking.status = 'cancelled'  # Use 'cancelled' as we don't have 'rejected' status
                    booking.save()
                    messages.success(request, f'Booking for {booking.room.name} has been rejected!')
                    
                elif action == 'cancel':
                    booking.status = 'cancelled'
                    booking.save()
                    messages.success(request, f'Booking for {booking.room.name} has been cancelled!')
                    
        except Booking.DoesNotExist:
            messages.error(request, 'Booking not found.')
        except Exception as e:
            messages.error(request, f'Booking action failed: {str(e)}')
    
    # Get all bookings
    try:
        from booking.models import Booking
        bookings = Booking.objects.all().order_by('-start_time')
        
        # Calculate statistics
        total_bookings = bookings.count()
        pending_bookings = bookings.filter(status='pending').count()
        confirmed_bookings = bookings.filter(status='confirmed').count()
        cancelled_bookings = bookings.filter(status='cancelled').count()
        
        # Get rooms for filtering
        rooms = []
        if bookings.exists():
            rooms = bookings.values_list('room', flat=True).distinct()
            from booking.models import Room
            rooms = Room.objects.filter(id__in=rooms)
        
    except ImportError:
        bookings = []
        rooms = []
        total_bookings = 0
        pending_bookings = 0
        confirmed_bookings = 0
        cancelled_bookings = 0

    context = {
        'user': request.user,
        'user_role': user_role,
        'bookings': bookings,
        'rooms': rooms,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    
    return render(request, 'AdminPage/allBookings.html', context)

@login_required
@admin_required
def admin_setting_view(request):
    """Admin settings - AdminPage/setting.html"""
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    user_role = get_user_role(request.user)
    form = None
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'change_password':
            # Handle password change
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Your password has been changed successfully!')
                return redirect('accounts:admin_setting')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif action == 'save_preferences':
            # Handle preferences save
            try:
                # Here you can save user preferences to user profile or settings model
                email_notifications = request.POST.get('email_notifications') == 'on'
                language = request.POST.get('language', 'en')
                date_format = request.POST.get('date_format', 'mm/dd/yyyy')
                
                # If you have a UserProfile model, save preferences there
                # For now, we'll just show success message
                messages.success(request, 'Preferences saved successfully!')
                return redirect('accounts:admin_setting')
            except Exception as e:
                messages.error(request, f'Failed to save preferences: {str(e)}')
        
        elif action == 'toggle_security':
            # Handle security toggles
            setting_name = request.POST.get('setting_name', '')
            enabled = request.POST.get('enabled') == 'true'
            
            # Here you can save security settings
            messages.success(request, f'{setting_name} {"enabled" if enabled else "disabled"} successfully!')
            return redirect('accounts:admin_setting')
    
    else:
        # GET request - create form
        form = PasswordChangeForm(request.user)
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'form': form,
    }
    
    return render(request, 'AdminPage/setting.html', context)

@login_required
@admin_required
def admin_profile_setting_view(request):
    """Admin profile - AdminPage/profileSetting.html"""
    user_role = get_user_role(request.user)
    
    if request.method == 'POST':
        try:
            # Update admin profile
            request.user.first_name = request.POST.get('firstName', '')
            request.user.last_name = request.POST.get('lastName', '')
            request.user.faculty = request.POST.get('faculty', '')
            request.user.department = request.POST.get('department', '')
            request.user.phone_number = request.POST.get('phoneNumber', '')
            
            # Handle password change
            current_password = request.POST.get('currentPassword')
            new_password = request.POST.get('newPassword')
            confirm_password = request.POST.get('confirmPassword')
            
            if new_password and confirm_password:
                if current_password and check_password(current_password, request.user.password):
                    if new_password == confirm_password:
                        request.user.set_password(new_password)
                        update_session_auth_hash(request, request.user)
                        messages.success(request, 'Profile and password updated successfully!')
                    else:
                        messages.error(request, 'New passwords do not match.')
                        return render(request, 'AdminPage/profileSetting.html', {'user': request.user})
                else:
                    messages.error(request, 'Current password is incorrect.')
                    return render(request, 'AdminPage/profileSetting.html', {'user': request.user})
            
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:admin_profile_setting')
            
        except Exception as e:
            messages.error(request, f'Profile update failed: {str(e)}')
    
    context = {
        'user': request.user,
        'user_role': user_role,
    }
    
    return render(request, 'AdminPage/profileSetting.html', context)

@login_required
def welcome_admin_view(request):
    """Welcome admin - AdminPage/welcomeAdmin.html"""
    user_role = get_user_role(request.user)
    
    if user_role != 'Admin':
        messages.error(request, 'Admin access required.')
        return redirect('accounts:user_dashboard')
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'full_name': f"{request.user.first_name} {request.user.last_name}",
    }
    
    return render(request, 'AdminPage/welcomeAdmin.html', context)

@login_required
@admin_required
def admin_about_us_view(request):
    """Admin about us - AdminPage/about-us.html"""
    user_role = get_user_role(request.user)
    
    context = {
        'user': request.user,
        'user_role': user_role,
    }
    
    return render(request, 'AdminPage/about-us.html', context)

@login_required
@admin_required
def admin_service_view(request):
    """Admin service/support - AdminPage/service.html"""
    user_role = get_user_role(request.user)
    
    # Handle admin contact form or support requests
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            # Save the support request or send email
            messages.success(request, 'Support request submitted successfully!')
            
        except Exception as e:
            messages.error(request, f'Failed to submit support request: {str(e)}')
    
    context = {
        'user': request.user,
        'user_role': user_role,
    }
    
    return render(request, 'AdminPage/service.html', context)

@login_required
@admin_required
def manage_users_view(request):
    """Manage users - AdminPage/manageUsers.html"""
    user_role = get_user_role(request.user)
    
    # Handle user management actions
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            user_id = request.POST.get('user_id')
            
            if action and user_id:
                target_user = User.objects.get(id=user_id)
                
                # Prevent users from modifying themselves
                if target_user.id == request.user.id:
                    messages.error(request, "You cannot modify your own account.")
                    return redirect('accounts:manage_users')
                
                if action == 'make_admin':
                    target_user.is_admin = True
                    target_user.save()
                    messages.success(request, f'User {target_user.get_full_name()} has been made an admin.')
                        
                elif action == 'make_user':
                    target_user.is_admin = False
                    target_user.save()
                    messages.success(request, f'User {target_user.get_full_name()} has been made a regular user.')
                        
                elif action == 'toggle_active':
                    target_user.is_active = not target_user.is_active
                    target_user.save()
                    status = 'activated' if target_user.is_active else 'deactivated'
                    messages.success(request, f'User {target_user.get_full_name()} has been {status}.')
                    
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'User management failed: {str(e)}')
        
        return redirect('accounts:manage_users')
    
    # Get all users
    try:
        all_users = User.objects.all().order_by('-date_joined')
        admin_users = all_users.filter(is_admin=True)
        regular_users = all_users.filter(is_admin=False)
        
        # Calculate statistics
        total_users = all_users.count()
        active_users = all_users.filter(is_active=True).count()
        inactive_users = total_users - active_users
        admin_count = admin_users.count()
        user_count = regular_users.count()
        
    except Exception as e:
        messages.error(request, f'Error loading users: {str(e)}')
        all_users = []
        admin_users = []
        regular_users = []
        total_users = 0
        active_users = 0
        inactive_users = 0
        admin_count = 0
        user_count = 0
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'all_users': all_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'admin_count': admin_count,
        'user_count': user_count,
    }
    
    return render(request, 'AdminPage/manageUsers.html', context)

@login_required
@admin_required
def admin_room_detail_view(request, room_id):
    """View room details for admin - AdminPage/roomDetail.html"""
    user_role = get_user_role(request.user)
    
    try:
        from booking.models import Room, Booking
        room = Room.objects.get(id=room_id)
        
        # Get room bookings
        bookings = Booking.objects.filter(room=room).order_by('-start_time')
        
        # Get today's bookings
        today = timezone.now().date()
        today_bookings = bookings.filter(start_time__date=today)
        
        # Get upcoming bookings
        upcoming_bookings = bookings.filter(
            start_time__gt=timezone.now(),
            status__in=['confirmed', 'pending']
        )[:10]
        
        # Get booking statistics
        total_bookings = bookings.count()
        confirmed_bookings = bookings.filter(status='confirmed').count()
        pending_bookings = bookings.filter(status='pending').count()
        cancelled_bookings = bookings.filter(status='cancelled').count()
        
        context = {
            'user': request.user,
            'user_role': user_role,
            'room': room,
            'bookings': bookings[:20],  # Limit to 20 recent bookings
            'today_bookings': today_bookings,
            'upcoming_bookings': upcoming_bookings,
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'pending_bookings': pending_bookings,
            'cancelled_bookings': cancelled_bookings,
        }
        
        return render(request, 'AdminPage/roomDetail.html', context)
        
    except Room.DoesNotExist:
        messages.error(request, 'Room not found.')
        return redirect('accounts:manage_rooms')
    except ImportError:
        messages.error(request, 'Room management system not available.')
        return redirect('accounts:admin_dashboard')
    except Exception as e:
        messages.error(request, f'Error loading room details: {str(e)}')
        return redirect('accounts:manage_rooms')

@login_required
@admin_required
def admin_add_room_view(request):
    """Add new room - AdminPage/addRoom.html"""
    user_role = get_user_role(request.user)
    
    try:
        from booking.models import Room
        
        if request.method == 'POST':
            # Get form data
            room_name = request.POST.get('room_name', '').strip()
            room_number = request.POST.get('room_number', '').strip()
            room_type = request.POST.get('room_type', '')
            capacity = request.POST.get('capacity', '')
            description = request.POST.get('description', '').strip()
            equipment = request.POST.get('equipment', '').strip()
            
            # Validation
            if not all([room_name, room_number, room_type, capacity]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'AdminPage/addRoom.html', {
                    'user': request.user,
                    'user_role': user_role,
                    'room_types': Room.ROOM_TYPES,
                })
            
            try:
                capacity = int(capacity)
                if capacity <= 0:
                    messages.error(request, 'Capacity must be a positive number.')
                    return render(request, 'AdminPage/addRoom.html', {
                        'user': request.user,
                        'user_role': user_role,
                        'room_types': Room.ROOM_TYPES,
                    })
            except ValueError:
                messages.error(request, 'Capacity must be a valid number.')
                return render(request, 'AdminPage/addRoom.html', {
                    'user': request.user,
                    'user_role': user_role,
                    'room_types': Room.ROOM_TYPES,
                })
            
            # Check if room number already exists
            if Room.objects.filter(room_number=room_number).exists():
                messages.error(request, f'Room number "{room_number}" already exists.')
                return render(request, 'AdminPage/addRoom.html', {
                    'user': request.user,
                    'user_role': user_role,
                    'room_types': Room.ROOM_TYPES,
                })
            
            # Create room
            room = Room.objects.create(
                name=room_name,
                room_number=room_number,
                room_type=room_type,
                capacity=capacity,
                description=description,
                equipment=equipment,
                is_available=True
            )
            
            messages.success(request, f'Room "{room_name}" ({room_number}) created successfully!')
            return redirect('accounts:manage_rooms')
        
        # GET request - show form
        context = {
            'user': request.user,
            'user_role': user_role,
            'room_types': Room.ROOM_TYPES,
            'action': 'add'
        }
        
        return render(request, 'AdminPage/admin_room_form.html', context)
        
    except ImportError:
        messages.error(request, 'Room management system not available.')
        return redirect('accounts:admin_dashboard')
    except Exception as e:
        messages.error(request, f'Error adding room: {str(e)}')
        return redirect('accounts:manage_rooms')

@login_required
@admin_required
def admin_edit_room_view(request, room_id):
    """Edit room - AdminPage/editRoom.html"""
    user_role = get_user_role(request.user)
    
    try:
        from booking.models import Room
        room = Room.objects.get(id=room_id)
        
        if request.method == 'POST':
            # Get form data
            room_name = request.POST.get('room_name', '').strip()
            room_number = request.POST.get('room_number', '').strip()
            room_type = request.POST.get('room_type', '')
            capacity = request.POST.get('capacity', '')
            description = request.POST.get('description', '').strip()
            equipment = request.POST.get('equipment', '').strip()
            
            # Validation
            if not all([room_name, room_number, room_type, capacity]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'AdminPage/editRoom.html', {
                    'user': request.user,
                    'user_role': user_role,
                    'room': room,
                    'room_types': Room.ROOM_TYPES,
                })
            
            try:
                capacity = int(capacity)
                if capacity <= 0:
                    messages.error(request, 'Capacity must be a positive number.')
                    return render(request, 'AdminPage/admin_room_form.html', {
                        'user': request.user,
                        'user_role': user_role,
                        'room': room,
                        'room_types': Room.ROOM_TYPES,
                        'action': 'edit'
                    })
            except ValueError:
                messages.error(request, 'Capacity must be a valid number.')
                return render(request, 'AdminPage/editRoom.html', {
                    'user': request.user,
                    'user_role': user_role,
                    'room': room,
                    'room_types': Room.ROOM_TYPES,
                })
            
            # Check if room number already exists (excluding current room)
            if Room.objects.filter(room_number=room_number).exclude(id=room_id).exists():
                messages.error(request, f'Room number "{room_number}" already exists.')
                return render(request, 'AdminPage/editRoom.html', {
                    'user': request.user,
                    'user_role': user_role,
                    'room': room,
                    'room_types': Room.ROOM_TYPES,
                })
            
            # Update room
            room.name = room_name
            room.room_number = room_number
            room.room_type = room_type
            room.capacity = capacity
            room.description = description
            room.equipment = equipment
            room.save()
            
            messages.success(request, f'Room "{room_name}" ({room_number}) updated successfully!')
            return redirect('accounts:manage_rooms')
        
        # GET request - show form
        context = {
            'user': request.user,
            'user_role': user_role,
            'room': room,
            'room_types': Room.ROOM_TYPES,
            'action': 'edit'
        }
        
        return render(request, 'AdminPage/admin_room_form.html', context)
        
    except Room.DoesNotExist:
        messages.error(request, 'Room not found.')
        return redirect('accounts:manage_rooms')
    except ImportError:
        messages.error(request, 'Room management system not available.')
        return redirect('accounts:admin_dashboard')
    except Exception as e:
        messages.error(request, f'Error editing room: {str(e)}')
        return redirect('accounts:manage_rooms')

@login_required
@admin_required
def admin_delete_room_view(request, room_id):
    """Delete room - AdminPage/deleteRoom.html"""
    user_role = get_user_role(request.user)
    
    try:
        from booking.models import Room, Booking
        room = Room.objects.get(id=room_id)
        
        if request.method == 'POST':
            # Check if room has active bookings
            active_bookings = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'pending'],
                start_time__gte=timezone.now()
            )
            
            if active_bookings.exists():
                messages.error(request, f'Cannot delete room "{room.name}". It has {active_bookings.count()} active booking(s).')
                return redirect('accounts:manage_rooms')
            
            # Delete room
            room_name = room.name
            room_number = room.room_number
            room.delete()
            
            messages.success(request, f'Room "{room_name}" ({room_number}) deleted successfully!')
            return redirect('accounts:manage_rooms')
        
        # GET request - show confirmation
        # Get room bookings for display
        bookings = Booking.objects.filter(room=room).order_by('-start_time')
        active_bookings = bookings.filter(
            status__in=['confirmed', 'pending'],
            start_time__gte=timezone.now()
        )
        
        context = {
            'user': request.user,
            'user_role': user_role,
            'room': room,
            'bookings': bookings[:10],  # Show recent bookings
            'active_bookings': active_bookings,
            'has_active_bookings': active_bookings.exists(),
        }
        
        return render(request, 'AdminPage/room_confirm_delete.html', context)
        
    except Room.DoesNotExist:
        messages.error(request, 'Room not found.')
        return redirect('accounts:manage_rooms')
    except ImportError:
        messages.error(request, 'Room management system not available.')
        return redirect('accounts:admin_dashboard')
    except Exception as e:
        messages.error(request, f'Error deleting room: {str(e)}')
        return redirect('accounts:manage_rooms')

# ============================================================================
# AJAX ENDPOINTS FOR ADMIN FUNCTIONALITY
# ============================================================================

@login_required
@admin_required
def ajax_change_user_role(request, user_id):
    """AJAX endpoint to change user role"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            action = data.get('action')
            
            target_user = User.objects.get(id=user_id)
            
            # Prevent admin from changing their own role
            if target_user == request.user:
                return JsonResponse({
                    'success': False, 
                    'error': 'You cannot change your own role.'
                })
            
            if action == 'make_admin':
                success = assign_user_role(target_user, 'Admin')
                if success:
                    return JsonResponse({
                        'success': True,
                        'message': f'User {target_user.email} has been made an admin.',
                        'user': {
                            'id': target_user.id,
                            'role': 'Admin',
                            'is_active': target_user.is_active
                        }
                    })
                else:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Failed to assign admin role.'
                    })
                    
            elif action == 'make_user':
                success = assign_user_role(target_user, 'User')
                if success:
                    return JsonResponse({
                        'success': True,
                        'message': f'User {target_user.email} has been made a regular user.',
                        'user': {
                            'id': target_user.id,
                            'role': 'User',
                            'is_active': target_user.is_active
                        }
                    })
                else:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Failed to assign user role.'
                    })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'Invalid action.'
                })
                
        except User.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'User not found.'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON data.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    })

@login_required
@admin_required
def ajax_toggle_user_status(request, user_id):
    """AJAX endpoint to toggle user active status"""
    if request.method == 'POST':
        try:
            target_user = User.objects.get(id=user_id)
            
            # Prevent admin from deactivating themselves
            if target_user == request.user:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': False, 
                        'error': 'You cannot deactivate your own account.'
                    })
                else:
                    messages.error(request, 'You cannot deactivate your own account.')
                    return redirect('accounts:manage_users')
            
            # Toggle active status
            target_user.is_active = not target_user.is_active
            target_user.save()
            
            status = 'activated' if target_user.is_active else 'deactivated'
            
            # Return JSON for AJAX requests
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f'User {target_user.email} has been {status}.',
                    'user': {
                        'id': target_user.id,
                        'role': get_user_role(target_user),
                        'is_active': target_user.is_active
                    }
                })
            else:
                # Return redirect for form submissions
                messages.success(request, f'User {target_user.email} has been {status}.')
                return redirect('accounts:manage_users')
                
        except User.DoesNotExist:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False, 
                    'error': 'User not found.'
                })
            else:
                messages.error(request, 'User not found.')
                return redirect('accounts:manage_users')
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False, 
                    'error': f'An error occurred: {str(e)}'
                })
            else:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('accounts:manage_users')
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    })

@login_required
@admin_required
def ajax_delete_room(request, room_id):
    """AJAX endpoint to delete a room"""
    if request.method == 'POST':
        try:
            from booking.models import Room
            room = Room.objects.get(id=room_id)
            room_name = room.name
            
            # Check if room has active bookings
            try:
                from booking.models import Booking
                active_bookings = Booking.objects.filter(
                    room=room,
                    status__in=['confirmed', 'pending'],
                    start_time__gte=timezone.now()
                )
                
                if active_bookings.exists():
                    return JsonResponse({
                        'success': False, 
                        'error': f'Cannot delete room "{room_name}". It has active bookings.'
                    })
            except:
                pass  # If booking model doesn't exist, skip check
            
            room.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Room "{room_name}" has been deleted successfully.'
            })
            
        except Room.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Room not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    })

@login_required
@admin_required
def ajax_toggle_room_availability(request, room_id):
    """AJAX endpoint to toggle room availability"""
    if request.method == 'POST':
        try:
            from booking.models import Room
            room = Room.objects.get(id=room_id)
            
            room.is_available = not room.is_available
            room.save()
            
            status = 'available' if room.is_available else 'unavailable'
            
            return JsonResponse({
                'success': True,
                'message': f'Room "{room.name}" is now {status}.',
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'is_available': room.is_available
                }
            })
            
        except Room.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Room not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    })

@login_required
@admin_required
def ajax_bulk_action(request):
    """AJAX endpoint for bulk actions on users/rooms"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            action = data.get('action')
            item_ids = data.get('item_ids', [])
            
            if not action or not item_ids:
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing action or item IDs.'
                })
            
            success_count = 0
            error_count = 0
            
            if action in ['make_admin', 'make_user', 'activate_users', 'deactivate_users']:
                # User bulk actions
                for user_id in item_ids:
                    try:
                        target_user = User.objects.get(id=user_id)
                        
                        # Skip current user
                        if target_user == request.user:
                            continue
                            
                        if action == 'make_admin':
                            if assign_user_role(target_user, 'Admin'):
                                success_count += 1
                            else:
                                error_count += 1
                        elif action == 'make_user':
                            if assign_user_role(target_user, 'User'):
                                success_count += 1
                            else:
                                error_count += 1
                        elif action == 'activate_users':
                            target_user.is_active = True
                            target_user.save()
                            success_count += 1
                        elif action == 'deactivate_users':
                            target_user.is_active = False
                            target_user.save()
                            success_count += 1
                            
                    except User.DoesNotExist:
                        error_count += 1
                    except Exception:
                        error_count += 1
                        
            elif action in ['activate_rooms', 'deactivate_rooms', 'delete_rooms']:
                # Room bulk actions
                try:
                    from booking.models import Room
                    for room_id in item_ids:
                        try:
                            room = Room.objects.get(id=room_id)
                            
                            if action == 'activate_rooms':
                                room.is_available = True
                                room.save()
                                success_count += 1
                            elif action == 'deactivate_rooms':
                                room.is_available = False
                                room.save()
                                success_count += 1
                            elif action == 'delete_rooms':
                                # Check for active bookings
                                try:
                                    from booking.models import Booking
                                    active_bookings = Booking.objects.filter(
                                        room=room,
                                        status__in=['confirmed', 'pending'],
                                        start_time__gte=timezone.now()
                                    )
                                    
                                    if not active_bookings.exists():
                                        room.delete()
                                        success_count += 1
                                    else:
                                        error_count += 1
                                except:
                                    room.delete()
                                    success_count += 1
                                    
                        except Room.DoesNotExist:
                            error_count += 1
                        except Exception:
                            error_count += 1
                except ImportError:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Room management not available.'
                    })
            
            return JsonResponse({
                'success': True,
                'message': f'Bulk action completed. {success_count} items processed successfully.',
                'details': {
                    'success_count': success_count,
                    'error_count': error_count
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON data.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'An error occurred: {str(e)}'
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    })

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_user_groups():
    """Setup User and Admin groups"""
    Group.objects.get_or_create(name='User')
    Group.objects.get_or_create(name='Admin')

def assign_user_role(user, role_name):
    """Assign User or Admin role"""
    try:
        user.groups.clear()
        group, created = Group.objects.get_or_create(name=role_name)
        user.groups.add(group)
        
        if role_name == 'Admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        
        user.save()
        print(f"Successfully assigned {role_name} role to {user.email}")
        return True
    except Exception as e:
        print(f"Error assigning role: {e}")
        return False

def get_user_role(user):
    """Get user role - User or Admin"""
    if not user.is_authenticated:
        return 'Unauthenticated'
    
    if user.groups.filter(name='Admin').exists():
        return 'Admin'
    elif user.groups.filter(name='User').exists():
        return 'User'
    else:
        # Default to User if no group assigned
        assign_user_role(user, 'User')
        return 'User'

# ============================================================================
# ADDITIONAL VIEWS
# ============================================================================

@login_required
@role_redirect
def dashboard_view(request):
    """Dashboard router"""
    pass  # This will be handled by the decorator

@login_required
def change_password_view(request):
    """Change password"""
    user_role = get_user_role(request.user)
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:setting')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    template = 'UserPage/setting.html' if user_role == 'User' else 'AdminPage/setting.html'
    context = {
        'form': form,
        'user': request.user,
        'user_role': user_role
    }
    return render(request, template, context)

# ============================================================================
# ADMIN MANAGEMENT FUNCTIONS (For creating admin accounts)
# ============================================================================

def create_admin_account(email, password, first_name, last_name):
    """Function to create admin account - can only be called from Django shell or management command"""
    try:
        if User.objects.filter(email=email).exists():
            print(f"Admin account {email} already exists")
            return False
        
        admin_user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            student_id=f"ADM{User.objects.count() + 1:04d}",
            phone_number="000-000-0000",
            faculty="Administration",
            department="IT Department"
        )
        
        setup_user_groups()
        assign_user_role(admin_user, 'Admin')
        
        print(f"Admin account created successfully: {email}")
        return True
        
    except Exception as e:
        print(f"Error creating admin account: {e}")
        return False

# Simple placeholder views
@login_required
def staff_dashboard_view(request):
    return redirect('accounts:admin_dashboard')

@login_required
def user_profile_view(request):
    return redirect('accounts:profile_setting')

@login_required
def update_notifications_view(request):
    """Update user notification preferences"""
    if request.method == 'POST':
        # Handle notification settings
        messages.success(request, 'Notification settings updated successfully!')
    
    user_role = get_user_role(request.user)
    if user_role == 'Admin':
        return redirect('accounts:admin_settings')
    else:
        return redirect('accounts:setting')

@login_required
def booking_detail_view(request, booking_id):
    """View booking details"""
    try:
        from booking.models import Booking
        booking = Booking.objects.get(id=booking_id, user=request.user)
        
        context = {
            'booking': booking,
            'user': request.user,
            'user_role': get_user_role(request.user),
        }
        
        return render(request, 'UserPage/booking-detail.html', context)
        
    except ImportError:
        messages.error(request, 'Booking system not available.')
        return redirect('accounts:booked')
    except:
        messages.error(request, 'Booking not found.')
        return redirect('accounts:booked')

# @login_required
# def make_admin_view(request):
#     """Make user admin - only for existing admins - DISABLED"""
#     # This function has been disabled as requested
#     messages.error(request, 'This functionality has been disabled.')
#     return redirect('accounts:admin_dashboard')


@login_required
def contact_support_view(request):
    """Handle contact support form submission"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Here you could save the contact message to a database model
        # or send an email to administrators
        # For now, just show a success message
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        
        return redirect('accounts:service')
    
    # If GET request, just redirect back to service page
    return redirect('accounts:service')

@login_required
def check_availability_ajax(request):
    """AJAX endpoint to check room availability"""
    if request.method == 'POST':
        try:
            from booking.models import Room, Booking
            import json
            
            data = json.loads(request.body)
            room_id = data.get('room_id')
            date = data.get('date')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            
            if not all([room_id, date, start_time, end_time]):
                return JsonResponse({'error': 'Missing required parameters'}, status=400)
            
            # Get room
            try:
                room = Room.objects.get(id=room_id)
            except Room.DoesNotExist:
                return JsonResponse({'available': False, 'message': 'Room not found'})
            
            # Check if room is available
            if not room.is_available:
                return JsonResponse({'available': False, 'message': 'Room is not available for booking'})
            
            # Parse date and time
            from datetime import datetime
            try:
                booking_date = datetime.strptime(date, '%Y-%m-%d').date()
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                
                start_datetime = datetime.combine(booking_date, start_time_obj)
                end_datetime = datetime.combine(booking_date, end_time_obj)
            except ValueError:
                return JsonResponse({'available': False, 'message': 'Invalid date or time format'})
            
            # Check if booking is in the future
            if start_datetime <= datetime.now():
                return JsonResponse({'available': False, 'message': 'Booking time must be in the future'})
            
            # Check if end time is after start time
            if start_datetime >= end_datetime:
                return JsonResponse({'available': False, 'message': 'End time must be after start time'})
            
            # Check for conflicts
            conflicts = Booking.objects.filter(
                room=room,
                start_time__lt=end_datetime,
                end_time__gt=start_datetime,
                status__in=['confirmed', 'pending']
            )
            
            if conflicts.exists():
                conflict = conflicts.first()
                conflict_time = conflict.start_time.strftime('%H:%M')
                return JsonResponse({
                    'available': False, 
                    'message': f'Time slot conflicts with existing booking at {conflict_time}',
                    'conflict': {
                        'start_time': conflict.start_time.strftime('%H:%M'),
                        'end_time': conflict.end_time.strftime('%H:%M'),
                        'user': conflict.user.get_full_name()
                    }
                })
            
            # Check daily booking limit
            daily_bookings = Booking.objects.filter(
                user=request.user,
                start_time__date=booking_date,
                status__in=['confirmed', 'pending']
            ).count()
            
            if daily_bookings >= 3:
                return JsonResponse({
                    'available': False, 
                    'message': 'You have reached the maximum number of bookings per day (3)'
                })
            
            # All checks passed
            return JsonResponse({
                'available': True, 
                'message': 'Room is available for booking',
                'room_info': {
                    'name': room.name,
                    'capacity': room.capacity,
                    'room_type': room.get_room_type_display(),
                    'equipment': room.equipment
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def get_rooms_ajax(request):
    """AJAX endpoint to get rooms for a specific building"""
    building_id = request.GET.get('building_id')
    room_type = request.GET.get('room_type', '')
    capacity_min = request.GET.get('capacity_min', '')
    
    try:
        from booking.models import Room
        
        # Start with available rooms
        rooms = Room.objects.filter(is_available=True)
        
        # Filter by building if provided
        if building_id:
            # Since we don't have a building relationship in our Room model,
            # we'll filter by room number prefix
            building_codes = {
                '1': 'A-',
                '2': 'S-',
                '3': 'L-',
                '4': 'B-',
            }
            if building_id in building_codes:
                rooms = rooms.filter(room_number__startswith=building_codes[building_id])
        
        # Filter by room type if provided
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        
        # Filter by minimum capacity if provided
        if capacity_min:
            try:
                capacity_min = int(capacity_min)
                rooms = rooms.filter(capacity__gte=capacity_min)
            except ValueError:
                pass
        
        rooms_data = []
        for room in rooms:
            try:
                # Get next booking for this room
                next_booking = room.bookings.filter(
                    start_time__gt=timezone.now(),
                    status__in=['confirmed', 'pending']
                ).order_by('start_time').first()
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'room_number': room.room_number,
                    'capacity': room.capacity,
                    'room_type': room.room_type,
                    'room_type_display': room.get_room_type_display(),
                    'description': room.description or '',
                    'equipment': room.equipment or '',
                    'location': f"{room.name} ({room.room_number})",
                    'available': room.is_available,
                    'next_booking': next_booking.start_time.strftime('%Y-%m-%d %H:%M') if next_booking else None
                })
            except Exception as e:
                # Skip this room if there's an error (e.g., missing field)
                continue
        
        return JsonResponse({'rooms': rooms_data})
        
    except ImportError:
        # Fallback data if booking models don't exist
        all_rooms = [
            {'id': 1, 'name': 'Conference Room A', 'room_number': 'A-201', 'capacity': 20, 'room_type': 'conference', 'room_type_display': 'Conference Room', 'description': 'Modern conference room', 'equipment': 'Projector, Whiteboard', 'location': 'Building A, Room 201', 'available': True, 'next_booking': None},
            {'id': 2, 'name': 'Computer Lab 1', 'room_number': 'A-206', 'capacity': 30, 'room_type': 'lab', 'room_type_display': 'Laboratory', 'description': 'Fully equipped computer lab', 'equipment': '30 PCs, Projector', 'location': 'Building A, Room 206', 'available': True, 'next_booking': None},
            {'id': 3, 'name': 'Lecture Hall', 'room_number': 'A-101', 'capacity': 100, 'room_type': 'classroom', 'room_type_display': 'Classroom', 'description': 'Large lecture hall', 'equipment': 'Audio system, Projector', 'location': 'Building A, Room 101', 'available': True, 'next_booking': None},
            {'id': 4, 'name': 'Chemistry Lab', 'room_number': 'S-309', 'capacity': 25, 'room_type': 'lab', 'room_type_display': 'Laboratory', 'description': 'Chemistry laboratory', 'equipment': 'Lab equipment, Safety gear', 'location': 'Building STEM, Room 309', 'available': True, 'next_booking': None},
            {'id': 5, 'name': 'Science Lab', 'room_number': 'S-205', 'capacity': 25, 'room_type': 'lab', 'room_type_display': 'Laboratory', 'description': 'Science laboratory', 'equipment': 'Lab equipment', 'location': 'Building STEM, Room 205', 'available': True, 'next_booking': None},
            {'id': 6, 'name': 'Meeting Room C', 'room_number': 'S-709', 'capacity': 12, 'room_type': 'conference', 'room_type_display': 'Conference Room', 'description': 'Small meeting room', 'equipment': 'TV, Conference phone', 'location': 'Building STEM, Room 709', 'available': True, 'next_booking': None},
            {'id': 7, 'name': 'Study Room 1', 'room_number': 'L-105', 'capacity': 8, 'room_type': 'study', 'room_type_display': 'Study Room', 'description': 'Quiet study room', 'equipment': 'Whiteboard, Tables', 'location': 'Library Building, Room 105', 'available': True, 'next_booking': None},
            {'id': 8, 'name': 'Business Classroom', 'room_number': 'B-301', 'capacity': 40, 'room_type': 'classroom', 'room_type_display': 'Classroom', 'description': 'Business school classroom', 'equipment': 'Projector, Whiteboard', 'location': 'Business Building, Room 301', 'available': True, 'next_booking': None},
        ]
        
        # Filter by building if provided
        if building_id:
            building_prefixes = {
                '1': 'A-',
                '2': 'S-',
                '3': 'L-',
                '4': 'B-',
            }
            if building_id in building_prefixes:
                prefix = building_prefixes[building_id]
                all_rooms = [room for room in all_rooms if room['room_number'].startswith(prefix)]
        
        # Filter by room type if provided
        if room_type:
            all_rooms = [room for room in all_rooms if room['room_type'] == room_type]
        
        # Filter by minimum capacity if provided
        if capacity_min:
            try:
                capacity_min = int(capacity_min)
                all_rooms = [room for room in all_rooms if room['capacity'] >= capacity_min]
            except ValueError:
                pass
        
        return JsonResponse({'rooms': all_rooms})

@login_required
def get_buildings_ajax(request):
    """AJAX endpoint to get all buildings"""
    try:
        from booking.models import Building
        
        buildings = Building.objects.all()
        buildings_data = []
        for building in buildings:
            buildings_data.append({
                'id': building.id,
                'name': building.name,
                'code': getattr(building, 'code', ''),
                'address': getattr(building, 'address', ''),
                'description': getattr(building, 'description', '')
            })
        
        return JsonResponse({'buildings': buildings_data})
        
    except ImportError:
        # Fallback if no Building model exists
        buildings_data = [
            {'id': 1, 'name': 'Building A', 'code': 'A', 'address': 'Main Campus', 'description': 'Main academic building'},
            {'id': 2, 'name': 'STEM Building', 'code': 'S', 'address': 'Science Campus', 'description': 'Science and technology building'},
            {'id': 3, 'name': 'Library Building', 'code': 'L', 'address': 'Central Campus', 'description': 'Main library with study rooms'},
            {'id': 4, 'name': 'Business Building', 'code': 'B', 'address': 'Business Campus', 'description': 'Business school building'}
        ]
        return JsonResponse({'buildings': buildings_data})


@login_required
@user_required
def cancel_booking_view(request, booking_id):
    """Cancel a booking"""
    user_role = get_user_role(request.user)
    
    try:
        from booking.models import Booking
        booking = Booking.objects.get(id=booking_id, user=request.user)
        
        if request.method == 'POST':
            # Check if booking can be cancelled
            if booking.status in ['pending', 'confirmed'] and booking.start_time > timezone.now():
                booking.status = 'cancelled'
                booking.save()
                
                messages.success(request, f'Booking for {booking.room.name} on {booking.start_time.strftime("%Y-%m-%d at %H:%M")} has been cancelled.')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Booking for {booking.room.name} has been cancelled.'
                    })
            else:
                error_msg = 'This booking cannot be cancelled.'
                messages.error(request, error_msg)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_msg
                    })
            
            return redirect('accounts:booked')
        
        # GET request - show confirmation page
        context = {
            'user': request.user,
            'user_role': user_role,
            'booking': booking,
            'can_cancel': booking.status in ['pending', 'confirmed'] and booking.start_time > timezone.now(),
        }
        
        return render(request, 'UserPage/cancelBooking.html', context)
        
    except Booking.DoesNotExist:
        messages.error(request, 'Booking not found.')
        return redirect('accounts:booked')
    except ImportError:
        messages.error(request, 'Booking system not available.')
        return redirect('accounts:booked')
    except Exception as e:
        messages.error(request, f'Error cancelling booking: {str(e)}')
        return redirect('accounts:booked')

@login_required
@user_required
def get_room_details_ajax(request):
    """AJAX endpoint to get room details for autofill"""
    room_id = request.GET.get('room_id')
    
    if not room_id:
        return JsonResponse({'success': False, 'error': 'Room ID is required'})
    
    try:
        from booking.models import Room
        
        room = Room.objects.get(id=room_id, is_available=True)
        
        return JsonResponse({
            'success': True,
            'room': {
                'id': room.id,
                'name': room.name,
                'room_number': room.room_number,
                'building_id': room.building.id if room.building else None,
                'building_name': room.building.name if room.building else None,
                'capacity': room.capacity,
                'room_type': room.room_type,
            }
        })
    
    except ImportError:
        # Fallback for when booking models don't exist
        fallback_rooms = {
            '1': {'id': 1, 'name': 'Room 101', 'room_number': 'A-101', 'building_id': 1, 'building_name': 'Building A'},
            '2': {'id': 2, 'name': 'Room 102', 'room_number': 'A-102', 'building_id': 1, 'building_name': 'Building A'},
            '3': {'id': 3, 'name': 'Room 201', 'room_number': 'B-201', 'building_id': 2, 'building_name': 'Building STEM'},
            '4': {'id': 4, 'name': 'Computer Lab 1', 'room_number': 'S-206', 'building_id': 2, 'building_name': 'Building STEM'},
            '5': {'id': 5, 'name': 'Study Room 1', 'room_number': 'L-105', 'building_id': 3, 'building_name': 'Library Building'},
        }
        
        if room_id in fallback_rooms:
            return JsonResponse({
                'success': True,
                'room': fallback_rooms[room_id]
            })
        else:
            return JsonResponse({'success': False, 'error': 'Room not found'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
@admin_required
def admin_booking_detail_view(request, booking_id):
    """Admin view for booking details"""
    user_role = get_user_role(request.user)
    
    try:
        from booking.models import Booking
        booking = Booking.objects.get(id=booking_id)
        
        context = {
            'booking': booking,
            'user': request.user,
            'user_role': user_role,
        }
        
        return render(request, 'AdminPage/booking-detail.html', context)
        
    except ImportError:
        messages.error(request, 'Booking system not available.')
        return redirect('accounts:all_bookings')
    except Booking.DoesNotExist:
        messages.error(request, 'Booking not found.')
        return redirect('accounts:all_bookings')
    except Exception as e:
        messages.error(request, f'Error viewing booking: {str(e)}')
        return redirect('accounts:all_bookings')
    
@login_required
@admin_required
def deactivate_user_view(request):
    """Deactivate user - only for existing admins"""
    user_role = get_user_role(request.user)
    
    if not request.user.is_admin:
        messages.error(request, 'Admin access required.')
        return redirect('accounts:user_dashboard')
    
    if request.method == 'POST':
        try:
            user_email = request.POST.get('user_email')
            action = request.POST.get('action')  # 'deactivate' or 'activate'
            
            if user_email:
                user = User.objects.get(email=user_email)
                
                # Prevent deactivating self
                if user.id == request.user.id:
                    messages.warning(request, 'You cannot deactivate your own account.')
                elif action == 'deactivate':
                    if not user.is_active:
                        messages.warning(request, f'User {user.get_full_name()} is already deactivated.')
                    else:
                        user.is_active = False
                        user.save()
                        messages.success(request, f'User {user.get_full_name()} has been deactivated.')
                elif action == 'activate':
                    if user.is_active:
                        messages.warning(request, f'User {user.get_full_name()} is already active.')
                    else:
                        user.is_active = True
                        user.save()
                        messages.success(request, f'User {user.get_full_name()} has been activated.')
            else:
                messages.error(request, 'Please provide a valid email address.')
                
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('accounts:deactivate_user')
    
    # Get all users for selection
    active_users = User.objects.filter(is_active=True).exclude(id=request.user.id).order_by('first_name', 'email')
    inactive_users = User.objects.filter(is_active=False).order_by('first_name', 'email')
    
    # Pre-select user if email is provided in GET parameters
    selected_user_email = request.GET.get('user_email', '')
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'selected_user_email': selected_user_email,
    }
    
    return render(request, 'AdminPage/deactivateUser.html', context)
