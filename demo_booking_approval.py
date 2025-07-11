#!/usr/bin/env python
"""
Demonstration of booking approval/rejection functionality
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from booking.models import Booking
from django.contrib.auth.models import Group

User = get_user_model()

def demonstrate_booking_approval():
    """Demonstrate the booking approval workflow"""
    print("=== BOOKING APPROVAL SYSTEM DEMONSTRATION ===\n")
    
    # Get pending bookings
    pending_bookings = Booking.objects.filter(status='pending')
    print(f"Found {pending_bookings.count()} pending bookings:\n")
    
    for booking in pending_bookings:
        print(f"📅 Booking ID: {booking.id}")
        print(f"   User: {booking.user.first_name} {booking.user.last_name} ({booking.user.email})")
        print(f"   Room: {booking.room.room_number} - {booking.room.room_type}")
        print(f"   Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')} - {booking.end_time.strftime('%H:%M')}")
        print(f"   Purpose: {booking.purpose}")
        print(f"   Attendees: {booking.attendees}")
        print(f"   Status: {booking.status}")
        print()
    
    # Show admin options
    print("🔧 ADMIN ACTIONS AVAILABLE:")
    print("   ✅ Approve booking (status -> 'confirmed')")
    print("   ❌ Reject booking (status -> 'cancelled')")
    print("   ⚠️  Cancel booking (status -> 'cancelled')")
    print("   👁️  View booking details")
    print()
    
    # Get admin users
    admin_group = Group.objects.get_or_create(name='Admin')[0]
    admin_users = User.objects.filter(groups=admin_group)
    print(f"👨‍💼 ADMIN USERS WHO CAN APPROVE/REJECT:")
    for admin in admin_users:
        print(f"   - {admin.email} ({admin.first_name} {admin.last_name})")
    print()
    
    # Show booking statistics
    total_bookings = Booking.objects.count()
    pending_count = Booking.objects.filter(status='pending').count()
    confirmed_count = Booking.objects.filter(status='confirmed').count()
    cancelled_count = Booking.objects.filter(status='cancelled').count()
    
    print("📊 BOOKING STATISTICS:")
    print(f"   Total bookings: {total_bookings}")
    print(f"   Pending approval: {pending_count}")
    print(f"   Confirmed: {confirmed_count}")
    print(f"   Cancelled: {cancelled_count}")
    print()
    
    # Show how to access admin interface
    print("🌐 ACCESS ADMIN INTERFACE:")
    print("   1. Go to: http://127.0.0.1:8000/accounts/login/")
    print("   2. Login with admin credentials:")
    print("      - Email: admin@rupp.edu.kh")
    print("      - Password: admin123")
    print("   3. Navigate to 'All Bookings' to approve/reject bookings")
    print("   4. Use 'Manage Rooms' to add/edit rooms with enhanced styling")
    print()
    
    print("=== FEATURES IMPLEMENTED ===")
    print("✅ Fixed timezone comparison error in booking creation")
    print("✅ Enhanced admin room form with modern CSS styling")
    print("✅ Improved booking approval interface with better UX")
    print("✅ Purpose field validation removed (users can select any purpose)")
    print("✅ Building selection works as dropdown")
    print("✅ Real-time booking approval/rejection with modal confirmations")
    print("✅ Responsive design for mobile and desktop")
    print("✅ Loading states and form validation")
    print("✅ Beautiful gradient styling and animations")

if __name__ == '__main__':
    demonstrate_booking_approval()
