# Phase four
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, time
from django.contrib.auth import get_user_model
from .models import Room, Booking, BookingRule, Announcement  

User = get_user_model()

from booking.utils import BookingRuleEnforcer
from .models import Room, Booking, BookingRule
from .forms import (
    RoomForm, RoomSearchForm, BookingForm, BookingSearchForm, 
    QuickBookingForm, BookingRuleForm, 
)
import json


@login_required
def room_list(request):
    """Display list of rooms with search and filtering"""
    
    # Get all rooms initially
    rooms = Room.objects.all().order_by('room_number')
    
    # Initialize search form
    search_form = RoomSearchForm(request.GET or None)
    
    if search_form.is_valid():
        # Apply search filters
        search_query = search_form.cleaned_data.get('search')
        room_type = search_form.cleaned_data.get('room_type')
        min_capacity = search_form.cleaned_data.get('min_capacity')
        max_capacity = search_form.cleaned_data.get('max_capacity')
        availability_date = search_form.cleaned_data.get('availability_date')
        start_time = search_form.cleaned_data.get('start_time')
        end_time = search_form.cleaned_data.get('end_time')
        available_only = search_form.cleaned_data.get('available_only')
        
        # Text search across name, room_number, and description
        if search_query:
            rooms = rooms.filter(
                Q(name__icontains=search_query) |
                Q(room_number__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by room type
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        
        # Filter by capacity range
        if min_capacity:
            rooms = rooms.filter(capacity__gte=min_capacity)
        if max_capacity:
            rooms = rooms.filter(capacity__lte=max_capacity)
        
        # Filter by availability status
        if available_only:
            rooms = rooms.filter(is_available=True)
        
        # Filter by date/time availability
        if availability_date and start_time and end_time:
            # Convert to datetime objects
            start_datetime = datetime.combine(availability_date, start_time)
            end_datetime = datetime.combine(availability_date, end_time)
            
            # Find rooms that don't have conflicting bookings
            conflicting_bookings = Booking.objects.filter(
                start_time__lt=end_datetime,
                end_time__gt=start_datetime,
                status__in=['confirmed', 'pending']
            ).values_list('room_id', flat=True)
            
            rooms = rooms.exclude(id__in=conflicting_bookings)
    
    # Pagination
    paginator = Paginator(rooms, 12)  # Show 12 rooms per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_rooms': paginator.count,
    }
    
    return render(request, 'UserPage/view_rooms.html', context)

@login_required
def room_detail(request, room_id):
    """Display detailed view of a room with availability"""
    
    room = get_object_or_404(Room, id=room_id)
    
    # Get current date and next 7 days for availability check
    today = timezone.now().date()
    next_week = today + timedelta(days=7)
    
    # Get bookings for the next week
    upcoming_bookings = Booking.objects.filter(
        room=room,
        start_time__date__range=[today, next_week],
        status__in=['confirmed', 'pending']
    ).order_by('start_time')
    
    # Check if room is available today
    today_bookings = upcoming_bookings.filter(start_time__date=today)
    
    context = {
        'room': room,
        'upcoming_bookings': upcoming_bookings,
        'today_bookings': today_bookings,
        'is_available_today': not today_bookings.exists() and room.is_available,
    }
    
    return render(request, 'UserPage/featureRoom.html', context)

@staff_member_required
def room_create(request):
    """Create a new room (Admin only)"""
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room "{room.name}" has been created successfully.')
            return redirect('bookings:room_detail', room_id=room.id)
    else:
        form = RoomForm()
    
    context = {
        'form': form,
        'title': 'Create New Room',
        'button_text': 'Create Room'
    }
    
    return render(request, 'AdminPage/manageRooms.html', context)

@staff_member_required
def room_edit(request, room_id):
    """Edit an existing room (Admin only)"""
    
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room "{room.name}" has been updated successfully.')
            return redirect('bookings:room_detail', room_id=room.id)
    else:
        form = RoomForm(instance=room)
    
    context = {
        'form': form,
        'room': room,
        'title': f'Edit Room: {room.name}',
        'button_text': 'Update Room'
    }
    
    return render(request, 'AdminPage/manageRooms.html', context)

@staff_member_required
def room_toggle_status(request, room_id):
    """Toggle room availability status (Admin only)"""
    
    if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id)
        room.is_available = not room.is_available
        room.save()
        
        status = 'available' if room.is_available else 'unavailable'
        messages.success(request, f'Room "{room.name}" has been marked as {status}.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'status': status,
                'is_available': room.is_available
            })
    
    return redirect('bookings:room_detail', room_id=room_id)

@staff_member_required
def admin_room_list(request):
    """Admin view for managing all rooms"""
    rooms = Room.objects.all().order_by('room_number')
    context = {
        'rooms': rooms
    }
    return render(request, 'AdminPage/manageRooms.html', context)

@staff_member_required
def room_delete(request, room_id):
    """Delete a room (Admin only)"""
    
    room = get_object_or_404(Room, id=room_id)
    
    # Check if room has any bookings
    has_bookings = Booking.objects.filter(room=room).exists()
    
    if request.method == 'POST':
        if has_bookings:
            messages.error(request, 'Cannot delete room with existing bookings.')
        else:
            room_name = room.name
            room.delete()
            messages.success(request, f'Room "{room_name}" has been deleted successfully.')
            return redirect('bookings:room_list')
    
    context = {
        'room': room,
        'has_bookings': has_bookings,
    }
    
    return render(request, 'AdminPage/manageRooms.html', context)

@login_required
def check_room_availability(request):
    """AJAX endpoint to check room availability for specific date/time"""
    
    if request.method == 'GET':
        room_id = request.GET.get('room_id')
        date = request.GET.get('date')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        if not all([room_id, date, start_time, end_time]):
            return JsonResponse({'error': 'Missing parameters'}, status=400)
        
        try:
            room = Room.objects.get(id=room_id)
            
            # Parse datetime
            availability_date = datetime.strptime(date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            start_datetime = datetime.combine(availability_date, start_time_obj)
            end_datetime = datetime.combine(availability_date, end_time_obj)
            
            # Check for conflicts
            conflicts = Booking.objects.filter(
                room=room,
                start_time__lt=end_datetime,
                end_time__gt=start_datetime,
                status__in=['confirmed', 'pending']
            )
            
            is_available = not conflicts.exists() and room.is_available
            
            conflict_details = []
            if conflicts.exists():
                for booking in conflicts:
                    conflict_details.append({
                        'start_time': booking.start_time.strftime('%H:%M'),
                        'end_time': booking.end_time.strftime('%H:%M'),
                        'purpose': booking.purpose,
                        'user': booking.user.get_full_name() or booking.user.email
                    })
            
            return JsonResponse({
                'available': is_available,
                'room_available': room.is_available,
                'conflicts': conflict_details
            })
            
        except Room.DoesNotExist:
            return JsonResponse({'error': 'Room not found'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid date/time format'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Duplicate create_booking function removed - keeping the one with email notifications
    
    return render(request, 'UserPage/booking.html', context)

@login_required
def user_bookings(request):
    """User's booking dashboard"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        bookings = bookings.filter(
            Q(room__name__icontains=search_query) |
            Q(purpose__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get booking statistics
    enforcer = BookingRuleEnforcer()
    stats = enforcer.get_user_booking_stats(request.user)
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'UserPage/booked.html', context)

@login_required
def booking_detail(request, booking_id):
    """Detailed view of a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if booking can be modified or cancelled
    enforcer = BookingRuleEnforcer()
    can_modify, modify_message = enforcer.can_modify_booking(booking)
    can_cancel, cancel_message = enforcer.rules.can_cancel_booking(booking) if enforcer.rules else (True, "")
    
    context = {
        'booking': booking,
        'can_modify': can_modify,
        'modify_message': modify_message,
        'can_cancel': can_cancel,
        'cancel_message': cancel_message,
    }
    
    return render(request, 'UserPage/booking-detail.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking_detail', booking_id=booking.id)
    
    # Check cancellation rules
    enforcer = BookingRuleEnforcer()
    if enforcer.rules:
        can_cancel, message = enforcer.rules.can_cancel_booking(booking)
        if not can_cancel:
            messages.error(request, message)
            return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('user_bookings')
    
    return render(request, 'UserPage/booked.html', {'booking': booking})

@login_required
def modify_booking(request, booking_id):
    """Modify an existing booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be modified.')
        return redirect('booking_detail', booking_id=booking.id)
    
    # Check modification rules
    enforcer = BookingRuleEnforcer()
    can_modify, message = enforcer.can_modify_booking(booking)
    if not can_modify:
        messages.error(request, message)
        return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking, user=request.user)
        if form.is_valid():
            modified_booking = form.save(commit=False)
            modified_booking.start_time = form.cleaned_data['start_datetime']
            modified_booking.end_time = form.cleaned_data['end_datetime']
            modified_booking.save()
            
            messages.success(request, 'Booking modified successfully.')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        # Populate form with existing booking data
        initial_data = {
            'start_date': booking.start_time.date(),
            'start_time': booking.start_time.time(),
            'end_time': booking.end_time.time(),
        }
        form = BookingForm(instance=booking, user=request.user, initial=initial_data)
    
    return render(request, 'UserPage/booking.html', {
        'form': form,
        'booking': booking
    })

@login_required
def booking_calendar(request):
    """Calendar view of user's bookings"""
    bookings = Booking.objects.filter(
        user=request.user,
        status__in=['pending', 'confirmed']
    ).select_related('room')
    
    # Convert bookings to calendar format
    calendar_events = []
    for booking in bookings:
        calendar_events.append({
            'id': booking.id,
            'title': f"{booking.room.name} - {booking.purpose[:30]}",
            'start': booking.start_time.isoformat(),
            'end': booking.end_time.isoformat(),
            'color': '#007bff' if booking.status == 'confirmed' else '#ffc107',
            'url': f"/bookings/{booking.id}/"
        })
    
    return render(request, 'UserPage/booking.html', {
        'calendar_events': calendar_events
    })

@require_http_methods(["POST"])
@login_required
def check_availability(request):
    """Real-time availability checking via AJAX"""
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        date_str = data.get('date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        if not all([room_id, date_str, start_time_str, end_time_str]):
            return JsonResponse({
                'available': False,
                'message': 'Missing required fields'
            })
        
        room = get_object_or_404(Room, id=room_id)
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        start_datetime = datetime.combine(booking_date, start_time)
        end_datetime = datetime.combine(booking_date, end_time)
        
        # Check if room is available
        if not room.is_available:
            return JsonResponse({
                'available': False,
                'message': 'Room is currently unavailable'
            })
        
        # Check for booking conflicts
        conflicts = Booking.objects.filter(
            room=room,
            date=booking_date,
            status__in=['confirmed', 'pending']
        ).filter(
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
        )

        if conflicts.exists():
            # Get suggested alternative times
            suggested_times = get_suggested_times(room, booking_date, start_time, end_time)
            return JsonResponse({
                'available': False,
                'message': 'Time slot conflicts with existing booking',
                'suggested_times': suggested_times
            })
        
        # Check booking rules
        rules_check = check_booking_rules(request.user, room, start_datetime, end_datetime)
        if not rules_check['valid']:
            return JsonResponse({
                'available': False,
                'message': rules_check['message']
            })
        
        return JsonResponse({
            'available': True,
            'message': 'Room is available for booking'
        })
        
    except Exception as e:
        return JsonResponse({
            'available': False,
            'message': f'Error checking availability: {str(e)}'
        })

@require_http_methods(["POST"])
@login_required
def check_conflicts(request):
    """Check for potential booking conflicts"""
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        date_str = data.get('date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        room = get_object_or_404(Room, id=room_id)
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # Get nearby bookings (within 1 hour before/after)
        extended_start = (datetime.combine(booking_date, start_time) - timedelta(hours=1)).time()
        extended_end = (datetime.combine(booking_date, end_time) + timedelta(hours=1)).time()
        
        nearby_bookings = Booking.objects.filter(
            room=room,
            date=booking_date,
            status__in=['confirmed', 'pending']
        ).filter(
            Q(start_time__gte=extended_start) | Q(end_time__lte=extended_end)
        ).values('start_time', 'end_time', 'purpose')
        
        conflicts = []
        for booking in nearby_bookings:
            if (booking['start_time'] < end_time and booking['end_time'] > start_time):
                conflicts.append({
                    'start_time': booking['start_time'].strftime('%H:%M'),
                    'end_time': booking['end_time'].strftime('%H:%M'),
                    'purpose': booking['purpose']
                })
        
        return JsonResponse({
            'conflicts': conflicts
        })
        
    except Exception as e:
        return JsonResponse({
            'conflicts': [],
            'error': str(e)
        })

def get_suggested_times(room, date, preferred_start, preferred_end):
    """Generate suggested available time slots"""
    duration = datetime.combine(date, preferred_end) - datetime.combine(date, preferred_start)
    duration_minutes = int(duration.total_seconds() / 60)
    
    # Get all bookings for the day
    existing_bookings = Booking.objects.filter(
        room=room,
        date=date,
        status__in=['confirmed', 'pending']
    ).order_by('start_time')
    
    # Define operating hours (8 AM to 10 PM)
    operating_start = time(8, 0)
    operating_end = time(22, 0)
    
    suggested_times = []
    current_time = operating_start
    
    for booking in existing_bookings:
        # Check if there's a gap before this booking
        if current_time < booking.start_time:
            potential_end = min(
                (datetime.combine(date, current_time) + timedelta(minutes=duration_minutes)).time(),
                booking.start_time
            )
            
            if (datetime.combine(date, potential_end) - datetime.combine(date, current_time)).total_seconds() >= duration_minutes * 60:
                suggested_times.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': potential_end.strftime('%H:%M')
                })
        
        current_time = max(current_time, booking.end_time)
        
        if len(suggested_times) >= 3:  # Limit suggestions
            break
    
    # Check for availability after last booking
    if current_time < operating_end and len(suggested_times) < 3:
        potential_end = min(
            (datetime.combine(date, current_time) + timedelta(minutes=duration_minutes)).time(),
            operating_end
        )
        
        if (datetime.combine(date, potential_end) - datetime.combine(date, current_time)).total_seconds() >= duration_minutes * 60:
            suggested_times.append({
                'start_time': current_time.strftime('%H:%M'),
                'end_time': potential_end.strftime('%H:%M')
            })
    
    return suggested_times

def check_booking_rules(user, room, start_datetime, end_datetime):
    """Check if booking complies with booking rules"""
    try:
        rules = BookingRule.objects.first()
        if not rules:
            return {'valid': True}
        
        # Check maximum duration
        duration = end_datetime - start_datetime
        if duration.total_seconds() / 3600 > rules.max_duration_hours:
            return {
                'valid': False,
                'message': f'Booking duration cannot exceed {rules.max_duration_hours} hours'
            }
        
        # Check daily limit
        today = start_datetime.date()
        today_bookings = Booking.objects.filter(
            user=user,
            date=today,
            status__in=['confirmed', 'pending']
        ).count()
        
        if today_bookings >= rules.daily_limit:
            return {
                'valid': False,
                'message': f'Daily booking limit of {rules.daily_limit} bookings exceeded'
            }
        
        # Check weekly limit
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        weekly_bookings = Booking.objects.filter(
            user=user,
            date__range=[week_start, week_end],
            status__in=['confirmed', 'pending']
        ).count()
        
        if weekly_bookings >= rules.weekly_limit:
            return {
                'valid': False,
                'message': f'Weekly booking limit of {rules.weekly_limit} bookings exceeded'
            }
        
        # Check advance booking limit
        now = timezone.now()
        advance_days = (start_datetime.date() - now.date()).days
        
        if advance_days > rules.advance_booking_days:
            return {
                'valid': False,
                'message': f'Cannot book more than {rules.advance_booking_days} days in advance'
            }
        
        return {'valid': True}
        
    except Exception as e:
        return {
            'valid': False,
            'message': f'Error checking booking rules: {str(e)}'
        }

@login_required
def user_dashboard(request):
    """Enhanced user dashboard with booking overview"""
    user = request.user
    
    # Get user's bookings
    upcoming_bookings = Booking.objects.filter(
        user=user,
        start_time__gt=timezone.now(),
        status__in=['confirmed', 'pending']
    ).order_by('start_time')[:5]
    
    past_bookings = Booking.objects.filter(
        user=user,
        end_time__lt=timezone.now()
    ).order_by('-end_time')[:5]
    
    # Get booking statistics
    total_bookings = Booking.objects.filter(user=user).count()
    confirmed_bookings = Booking.objects.filter(user=user, status='confirmed').count()
    pending_bookings = Booking.objects.filter(user=user, status='pending').count()
    cancelled_bookings = Booking.objects.filter(user=user, status='cancelled').count()
    
    # Get available rooms
    available_rooms = Room.objects.filter(
        is_available=True,
        availability_status='available'
    ).count()
    
    # Recent activity
    recent_activity = Booking.objects.filter(
        user=user
    ).order_by('-created_at')[:10]
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'available_rooms': available_rooms,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'UserPage/welcomeUser.html', context)

@login_required
def room_list(request):
    """Display available rooms with search and filtering"""
    rooms = Room.objects.filter(is_available=True).order_by('room_number')
    
    # Search functionality
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
    
    # Filter by capacity
    min_capacity = request.GET.get('min_capacity')
    if min_capacity:
        try:
            rooms = rooms.filter(capacity__gte=int(min_capacity))
        except ValueError:
            pass
    
    # Filter by availability status
    availability_status = request.GET.get('availability_status', '')
    if availability_status:
        rooms = rooms.filter(availability_status=availability_status)
    
    # Pagination
    paginator = Paginator(rooms, 12)
    page = request.GET.get('page')
    rooms = paginator.get_page(page)
    
    context = {
        'rooms': rooms,
        'room_types': Room.ROOM_TYPES,
        'search_query': search_query,
        'selected_room_type': room_type,
        'selected_availability_status': availability_status,
        'min_capacity': min_capacity,
    }
    
    return render(request, 'UserPage/featureRoom.html', context)

@login_required
def room_detail(request, room_id):
    """Display detailed room information with booking option"""
    room = get_object_or_404(Room, id=room_id)
    
    # Get today's bookings for this room
    today = timezone.now().date()
    today_bookings = Booking.objects.filter(
        room=room,
        start_time__date=today,
        status__in=['confirmed', 'pending']
    ).order_by('start_time')
    
    # Get upcoming bookings (next 7 days)
    upcoming_bookings = Booking.objects.filter(
        room=room,
        start_time__gte=timezone.now(),
        start_time__date__lte=today + timedelta(days=7),
        status__in=['confirmed', 'pending']
    ).order_by('start_time')[:10]
    
    # Check if user can book this room
    can_book = room.is_bookable()
    
    context = {
        'room': room,
        'today_bookings': today_bookings,
        'upcoming_bookings': upcoming_bookings,
        'can_book': can_book,
        'booking_form': BookingForm(),
    }
    
    return render(request, 'UserPage/room_detail.html', context)

@login_required
def create_booking(request):
    """Create a new booking"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            
            try:
                booking.save()
                messages.success(request, 'Booking created successfully! Please wait for confirmation.')
                return redirect('booking:user_bookings')
            except Exception as e:
                messages.error(request, f'Error creating booking: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()
    
    # Get available rooms
    rooms = Room.objects.filter(is_available=True, availability_status='available')
    
    context = {
        'form': form,
        'rooms': rooms,
    }
    
    return render(request, 'UserPage/booking.html', context)

@login_required
def user_bookings(request):
    """Display user's bookings with filtering"""
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by date range
    date_filter = request.GET.get('date_filter', '')
    if date_filter == 'upcoming':
        bookings = bookings.filter(start_time__gte=timezone.now())
    elif date_filter == 'past':
        bookings = bookings.filter(end_time__lt=timezone.now())
    elif date_filter == 'today':
        today = timezone.now().date()
        bookings = bookings.filter(start_time__date=today)
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page = request.GET.get('page')
    bookings = paginator.get_page(page)
    
    context = {
        'bookings': bookings,
        'booking_statuses': Booking.STATUS_CHOICES,
        'selected_status': status,
        'selected_date_filter': date_filter,
    }
    
    return render(request, 'UserPage/booked.html', context)

@login_required
def booking_detail(request, booking_id):
    """Display booking details"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'UserPage/booking-detail.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if not booking.can_cancel():
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking:booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('booking:user_bookings')
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'UserPage/cancel_booking.html', context)

@login_required
def check_room_availability(request):
    """AJAX endpoint to check room availability"""
    room_id = request.GET.get('room_id')
    date = request.GET.get('date')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    
    if not all([room_id, date, start_time, end_time]):
        return JsonResponse({'error': 'All parameters are required'}, status=400)
    
    try:
        room = Room.objects.get(id=room_id)
        
        # Parse datetime
        start_datetime = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')
        
        # Make timezone aware
        start_datetime = timezone.make_aware(start_datetime)
        end_datetime = timezone.make_aware(end_datetime)
        
        # Check if room is available
        is_available = room.is_available_at(start_datetime, end_datetime)
        
        return JsonResponse({
            'available': is_available,
            'room_name': room.name,
            'message': 'Room is available' if is_available else 'Room is not available for the selected time'
        })
        
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)
    except ValueError as e:
        return JsonResponse({'error': f'Invalid date/time format: {str(e)}'}, status=400)

@login_required
def quick_book(request, room_id):
    """Quick booking for a specific room"""
    room = get_object_or_404(Room, id=room_id)
    
    if not room.is_bookable():
        messages.error(request, 'This room is not available for booking.')
        return redirect('booking:room_detail', room_id=room_id)
    
    if request.method == 'POST':
        form = QuickBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            
            try:
                booking.save()
                messages.success(request, 'Booking created successfully!')
                return redirect('booking:booking_detail', booking_id=booking.id)
            except Exception as e:
                messages.error(request, f'Error creating booking: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuickBookingForm()
    
    context = {
        'form': form,
        'room': room,
    }
    
    return render(request, 'UserPage/quick_book.html', context)

@login_required
def booking_calendar(request):
    """Display booking calendar view"""
    # Get all confirmed bookings
    bookings = Booking.objects.filter(
        status='confirmed',
        start_time__gte=timezone.now() - timedelta(days=30)
    ).select_related('room', 'user')
    
    # Format bookings for calendar
    calendar_events = []
    for booking in bookings:
        calendar_events.append({
            'id': booking.id,
            'title': f"{booking.room.name} - {booking.user.get_full_name()}",
            'start': booking.start_time.isoformat(),
            'end': booking.end_time.isoformat(),
            'backgroundColor': '#007bff',
            'textColor': '#ffffff',
            'url': f"/booking/{booking.id}/"
        })
    
    context = {
        'calendar_events': json.dumps(calendar_events),
    }
    
    return render(request, 'UserPage/booking_calendar.html', context)

# Additional API functions
@login_required
def rooms_api_availability(request):
    """API endpoint to get room availability information"""
    rooms = Room.objects.filter(is_available=True)
    
    # Get date parameter
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            room_data = []
            for room in rooms:
                # Get bookings for this room on the target date
                bookings = Booking.objects.filter(
                    room=room,
                    start_time__date=target_date,
                    status__in=['confirmed', 'pending']
                ).order_by('start_time')
                
                booking_slots = []
                for booking in bookings:
                    booking_slots.append({
                        'start': booking.start_time.strftime('%H:%M'),
                        'end': booking.end_time.strftime('%H:%M'),
                        'status': booking.status,
                        'user': booking.user.get_full_name(),
                    })
                
                room_data.append({
                    'id': room.id,
                    'name': room.name,
                    'room_number': room.room_number,
                    'capacity': room.capacity,
                    'room_type': room.get_room_type_display(),
                    'is_bookable': room.is_bookable(),
                    'bookings': booking_slots,
                })
            
            return JsonResponse({
                'success': True,
                'date': date_str,
                'rooms': room_data
            })
            
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    
    # Return basic room info if no date specified
    room_data = []
    for room in rooms:
        room_data.append({
            'id': room.id,
            'name': room.name,
            'room_number': room.room_number,
            'capacity': room.capacity,
            'room_type': room.get_room_type_display(),
            'is_bookable': room.is_bookable(),
        })
    
    return JsonResponse({
        'success': True,
        'rooms': room_data
    })

@login_required
def check_availability(request):
    """Check availability for multiple parameters"""
    return check_room_availability(request)

@login_required
def modify_booking(request, booking_id):
    """Modify an existing booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if not booking.can_be_modified():
        messages.error(request, 'This booking cannot be modified.')
        return redirect('booking:booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            try:
                booking = form.save()
                messages.success(request, 'Booking modified successfully!')
                return redirect('booking:booking_detail', booking_id=booking.id)
            except Exception as e:
                messages.error(request, f'Error modifying booking: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm(instance=booking)
    
    context = {
        'form': form,
        'booking': booking,
    }
    
    return render(request, 'UserPage/modify_booking.html', context)

