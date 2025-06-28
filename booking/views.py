from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Room, Booking
from .forms import RoomForm, RoomSearchForm


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
    
    return render(request, 'bookings/room_list.html', context)


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
    
    return render(request, 'bookings/room_detail.html', context)


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
    
    return render(request, 'bookings/room_form.html', context)


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
    
    return render(request, 'bookings/room_form.html', context)


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
    
    return render(request, 'bookings/room_delete.html', context)


# AJAX view for checking room availability
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
