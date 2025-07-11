# booking/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Room, Booking, BookingRule, Announcement
from .forms import RoomForm, BookingRuleForm, AnnouncementForm, AdminBookingForm
from .decorators import admin_required
from accounts.models import User
import json

@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with system statistics"""
    # Get statistics
    total_rooms = Room.objects.count()
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(
        status='confirmed',
        end_time__gte=timezone.now()
    ).count()
    
    # Pending bookings that need approval
    pending_bookings = Booking.objects.filter(status='pending').count()
    
    # Today's bookings
    today = timezone.now().date()
    today_bookings = Booking.objects.filter(
        start_time__date=today,
        status='confirmed'
    ).count()
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related('user', 'room').order_by('-created_at')[:10]
    
    # Room utilization stats
    room_stats = Room.objects.annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')[:5]
    
    # Users statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_count = User.objects.filter(is_admin=True).count()
    staff_count = User.objects.filter(is_staff=True, is_admin=False).count()
    regular_count = total_users - admin_count - staff_count
    
    # Get most booked rooms
    most_booked_rooms = Room.objects.annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')[:5]
    
    # Get upcoming bookings
    upcoming_bookings = Booking.objects.filter(
        start_time__gt=timezone.now(),
        status='confirmed'
    ).order_by('start_time')[:5]
    
    context = {
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'today_bookings': today_bookings,
        'recent_bookings': recent_bookings,
        'room_stats': room_stats,
        'total_users': total_users,
        'active_users': active_users,
        'admin_count': admin_count,
        'staff_count': staff_count,
        'regular_count': regular_count,
        'most_booked_rooms': most_booked_rooms,
        'upcoming_bookings': upcoming_bookings,
    }
    
    return render(request, 'AdminPage/adminHomePage.html', context)

# Step 19: Admin Room Management
@login_required
@admin_required
def admin_room_list(request):
    """Admin room management with search and filtering"""
    rooms = Room.objects.all().order_by('room_number')
    
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
    
    # Filter by availability
    availability = request.GET.get('availability', '')
    if availability:
        rooms = rooms.filter(availability_status=availability)
    
    # Pagination
    paginator = Paginator(rooms, 10)
    page = request.GET.get('page')
    rooms = paginator.get_page(page)
    
    room_types = Room.ROOM_TYPES
    availability_statuses = Room.AVAILABILITY_STATUS
    
    context = {
        'rooms': rooms,
        'search_query': search_query,
        'room_types': room_types,
        'availability_statuses': availability_statuses,
        'selected_room_type': room_type,
        'selected_availability': availability,
    }
    
    return render(request, 'AdminPage/manageRooms.html', context)

@login_required
@admin_required
def admin_room_create(request):
    """Create new room"""
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room "{room.name}" created successfully!')
            return redirect('booking:admin_room_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoomForm()
    
    return render(request, 'AdminPage/room_form.html', {
        'form': form,
        'title': 'Create New Room',
        'action': 'Create'
    })

@login_required
@admin_required
def admin_room_edit(request, room_id):
    """Edit existing room"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room "{room.name}" updated successfully!')
            return redirect('booking:admin_room_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'AdminPage/room_form.html', {
        'form': form,
        'room': room,
        'title': f'Edit Room - {room.name}',
        'action': 'Update'
    })

@login_required
@admin_required
def admin_room_delete(request, room_id):
    """Delete room"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        room_name = room.name
        room.delete()
        messages.success(request, f'Room "{room_name}" deleted successfully!')
        return redirect('booking:admin_room_list')
    
    # Check if room has active bookings
    active_bookings = Booking.objects.filter(
        room=room,
        status__in=['confirmed', 'pending'],
        end_time__gte=timezone.now()
    ).count()
    
    return render(request, 'AdminPage/room_confirm_delete.html', {
        'room': room,
        'active_bookings': active_bookings,
    })

@login_required
@admin_required
def admin_room_toggle_availability(request, room_id):
    """Toggle room availability status"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Room.AVAILABILITY_STATUS):
            room.availability_status = new_status
            room.save()
            messages.success(request, f'Room "{room.name}" status updated to {room.get_availability_status_display()}.')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('booking:admin_room_list')

@login_required
@admin_required
def admin_room_bulk_action(request):
    """Perform bulk actions on rooms"""
    if request.method == 'POST':
        action = request.POST.get('action')
        room_ids = request.POST.getlist('room_ids')
        
        if not room_ids:
            messages.error(request, 'Please select at least one room.')
            return redirect('booking:admin_room_list')
        
        rooms = Room.objects.filter(id__in=room_ids)
        
        if action == 'delete':
            count = rooms.count()
            rooms.delete()
            messages.success(request, f'{count} rooms deleted successfully!')
        
        elif action == 'set_available':
            rooms.update(availability_status='available')
            messages.success(request, f'{rooms.count()} rooms set to available.')
        
        elif action == 'set_maintenance':
            rooms.update(availability_status='maintenance')
            messages.success(request, f'{rooms.count()} rooms set to maintenance.')
        
        elif action == 'set_unavailable':
            rooms.update(availability_status='unavailable')
            messages.success(request, f'{rooms.count()} rooms set to unavailable.')
    
    return redirect('booking:admin_room_list')

# Step 20: Admin Booking Oversight
@login_required
@admin_required
def admin_booking_list(request):
    """Admin booking management with comprehensive filtering"""
    bookings = Booking.objects.select_related('user', 'room').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        bookings = bookings.filter(start_time__gte=date_from)
    if date_to:
        bookings = bookings.filter(start_time__lte=date_to)
    
    # Filter by room
    room_id = request.GET.get('room')
    if room_id:
        bookings = bookings.filter(room_id=room_id)
    
    # Filter by user
    user_id = request.GET.get('user')
    if user_id:
        bookings = bookings.filter(user_id=user_id)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        bookings = bookings.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(room__name__icontains=search_query) |
            Q(room__room_number__icontains=search_query) |
            Q(purpose__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(bookings, 15)
    page = request.GET.get('page')
    bookings = paginator.get_page(page)
    
    # Get filter options
    rooms = Room.objects.all().order_by('room_number')
    users = User.objects.filter(is_active=True).order_by('first_name')
    
    context = {
        'bookings': bookings,
        'rooms': rooms,
        'users': users,
        'booking_statuses': Booking.STATUS_CHOICES,
        'selected_status': status,
        'selected_room': room_id,
        'selected_user': user_id,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
    }
    
    return render(request, 'AdminPage/allBookings.html', context)

@login_required
@admin_required
def admin_booking_create(request):
    """Admin create booking for users"""
    if request.method == 'POST':
        form = AdminBookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f'Booking created successfully for {booking.user.get_full_name()}!')
            return redirect('booking:admin_booking_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminBookingForm()
    
    return render(request, 'AdminPage/admin_booking_form.html', {
        'form': form,
        'title': 'Create New Booking',
        'action': 'Create'
    })

@login_required
@admin_required
def admin_booking_edit(request, booking_id):
    """Admin edit booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        form = AdminBookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f'Booking updated successfully!')
            return redirect('booking:admin_booking_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminBookingForm(instance=booking)
    
    return render(request, 'AdminPage/admin_booking_form.html', {
        'form': form,
        'booking': booking,
        'title': f'Edit Booking #{booking.id}',
        'action': 'Update'
    })

@login_required
@admin_required
def admin_booking_delete(request, booking_id):
    """Admin delete booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        booking_info = f"#{booking.id} - {booking.room.name}"
        booking.delete()
        messages.success(request, f'Booking {booking_info} deleted successfully!')
        return redirect('booking:admin_booking_list')
    
    return render(request, 'AdminPage/booking_confirm_delete.html', {
        'booking': booking,
    })

@login_required
@admin_required
def admin_booking_update_status(request, booking_id):
    """Update booking status"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Booking.STATUS_CHOICES]:
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('admin_booking_list')

# Step 21: System Configuration
@login_required
@admin_required
def admin_booking_rules(request):
    """Admin manage booking rules"""
    rules = BookingRule.objects.all().order_by('-is_active', 'name')
    
    if request.method == 'POST':
        form = BookingRuleForm(request.POST)
        if form.is_valid():
            rule = form.save()
            messages.success(request, f'Booking rule "{rule.name}" created successfully!')
            return redirect('booking:admin_booking_rules')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingRuleForm()
    
    context = {
        'rules': rules,
        'form': form,
    }
    
    return render(request, 'AdminPage/booking_rules.html', context)

@login_required
@admin_required
def admin_announcements(request):
    """Admin manage announcements"""
    announcements = Announcement.objects.all().order_by('-created_at')
    
    context = {
        'announcements': announcements,
    }
    
    return render(request, 'AdminPage/announcements.html', context)

@login_required
@admin_required
def admin_announcement_create(request):
    """Admin create announcement"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save()
            messages.success(request, f'Announcement "{announcement.title}" created successfully!')
            return redirect('booking:admin_announcements')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AnnouncementForm()
    
    return render(request, 'AdminPage/announcement_form.html', {
        'form': form,
        'title': 'Create New Announcement',
        'action': 'Create'
    })

@login_required
@admin_required
def admin_announcement_edit(request, announcement_id):
    """Admin edit announcement"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            announcement = form.save()
            messages.success(request, f'Announcement "{announcement.title}" updated successfully!')
            return redirect('booking:admin_announcements')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'AdminPage/announcement_form.html', {
        'form': form,
        'announcement': announcement,
        'title': f'Edit Announcement - {announcement.title}',
        'action': 'Update'
    })

@login_required
@admin_required
def admin_announcement_delete(request, announcement_id):
    """Admin delete announcement"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        title = announcement.title
        announcement.delete()
        messages.success(request, f'Announcement "{title}" deleted successfully!')
        return redirect('booking:admin_announcements')
    
    return render(request, 'AdminPage/announcement_confirm_delete.html', {
        'announcement': announcement,
    })

@login_required
@admin_required
def admin_announcement_toggle_active(request, announcement_id):
    """Toggle announcement active status"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        announcement.is_active = not announcement.is_active
        announcement.save()
        
        status = 'activated' if announcement.is_active else 'deactivated'
        messages.success(request, f'Announcement "{announcement.title}" {status} successfully.')
    
    return redirect('booking:admin_announcements')

@login_required
@admin_required
def admin_user_management(request):
    """Admin user management"""
    
    # Handle POST requests for user role/status changes
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        if action and user_id:
            try:
                target_user = get_object_or_404(User, id=user_id)
                
                # Prevent users from modifying themselves
                if target_user.id == request.user.id:
                    messages.error(request, "You cannot modify your own account.")
                    return redirect('booking:admin_user_management')
                
                if action == 'make_admin':
                    target_user.is_admin = True
                    target_user.save()
                    messages.success(request, f'"{target_user.get_full_name()}" is now an administrator.')
                    
                elif action == 'make_user':
                    target_user.is_admin = False
                    target_user.save()
                    messages.success(request, f'"{target_user.get_full_name()}" is now a regular user.')
                    
                elif action == 'toggle_active':
                    target_user.is_active = not target_user.is_active
                    status = 'activated' if target_user.is_active else 'deactivated'
                    target_user.save()
                    messages.success(request, f'"{target_user.get_full_name()}" has been {status}.')
                    
            except User.DoesNotExist:
                messages.error(request, "User not found.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        
        return redirect('booking:admin_user_management')
    
    # GET request - display users
    all_users = User.objects.all().order_by('first_name')
    
    # Calculate statistics
    total_users = all_users.count()
    active_users = all_users.filter(is_active=True).count()
    admin_count = all_users.filter(is_admin=True).count()
    user_count = all_users.filter(is_admin=False).count()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        all_users = all_users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )
    
    # Filter by role
    role = request.GET.get('role', '')
    if role == 'admin':
        all_users = all_users.filter(is_admin=True)
    elif role == 'staff':
        all_users = all_users.filter(is_staff=True, is_admin=False)
    elif role == 'user':
        all_users = all_users.filter(is_admin=False, is_staff=False)
    
    # Filter by active status
    active = request.GET.get('active', '')
    if active == 'true':
        all_users = all_users.filter(is_active=True)
    elif active == 'false':
        all_users = all_users.filter(is_active=False)
    
    context = {
        'all_users': all_users,
        'total_users': total_users,
        'active_users': active_users,
        'admin_count': admin_count,
        'user_count': user_count,
        'search_query': search_query,
        'selected_role': role,
        'selected_active': active,
    }
    
    return render(request, 'AdminPage/manageUsers.html', context)

@login_required
@admin_required
def admin_user_toggle_status(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User "{user.get_full_name()}" {status} successfully.')
    
    return redirect('booking:admin_user_management')

# API endpoints for admin
@login_required
@admin_required
def admin_get_room_availability(request):
    """Get room availability for admin dashboard"""
    room_id = request.GET.get('room_id')
    date = request.GET.get('date')
    
    if not room_id or not date:
        return JsonResponse({'error': 'Room ID and date are required'}, status=400)
    
    try:
        room = Room.objects.get(id=room_id)
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get bookings for the specific date
        bookings = Booking.objects.filter(
            room=room,
            start_time__date=target_date,
            status__in=['confirmed', 'pending']
        ).order_by('start_time')
        
        booking_data = []
        for booking in bookings:
            booking_data.append({
                'id': booking.id,
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'user': booking.user.get_full_name(),
                'purpose': booking.purpose,
                'status': booking.status,
            })
        
        return JsonResponse({
            'success': True,
            'room': room.name,
            'date': date,
            'bookings': booking_data
        })
        
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

@login_required
@admin_required
def admin_booking_stats(request):
    """Get booking statistics for admin dashboard"""
    # Get date range
    days = int(request.GET.get('days', 7))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get bookings in date range
    bookings = Booking.objects.filter(
        created_at__date__range=[start_date, end_date]
    )
    
    # Group by date
    daily_stats = {}
    for booking in bookings:
        date_str = booking.created_at.strftime('%Y-%m-%d')
        if date_str not in daily_stats:
            daily_stats[date_str] = {
                'total': 0,
                'confirmed': 0,
                'pending': 0,
                'cancelled': 0,
                'rejected': 0,
            }
        daily_stats[date_str]['total'] += 1
        daily_stats[date_str][booking.status] += 1
    
    return JsonResponse({
        'success': True,
        'daily_stats': daily_stats,
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
        }
    })