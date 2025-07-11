# booking/email_utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def send_booking_confirmation_email(booking):
    """Send booking confirmation email to user"""
    try:
        subject = f"Booking Confirmed - {booking.room.name}"
        
        message = f"""
Hello {booking.user.first_name}!

Your room booking has been confirmed successfully. Here are the details:

Room: {booking.room.name} ({booking.room.room_number})
Date: {booking.start_time.strftime('%B %d, %Y')}
Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
Duration: {booking.duration} hours
Purpose: {booking.purpose}
Status: {booking.get_status_display()}

Important Notes:
- Please arrive on time for your booking
- Remember to bring your student ID
- You can cancel your booking up to 2 hours before the start time
- If you need to modify your booking, please contact us

Thank you for using our Room Booking System!

This is an automated email. Please do not reply to this email.
If you have any questions, please contact our support team.
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Booking confirmation email sent to {booking.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send booking confirmation email: {str(e)}")
        return False

def send_booking_cancellation_email(booking):
    """Send booking cancellation email to user"""
    try:
        subject = f"Booking Cancelled - {booking.room.name}"
        
        message = f"""
Hello {booking.user.first_name}!

Your room booking has been cancelled. Here are the details of the cancelled booking:

Room: {booking.room.name} ({booking.room.room_number})
Date: {booking.start_time.strftime('%B %d, %Y')}
Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
Purpose: {booking.purpose}
Status: {booking.get_status_display()}

The room is now available for other users to book.

You can make a new booking anytime through our Room Booking System.

Thank you for using our Room Booking System!

This is an automated email. Please do not reply to this email.
If you have any questions, please contact our support team.
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Booking cancellation email sent to {booking.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send booking cancellation email: {str(e)}")
        return False

def send_booking_reminder_email(booking):
    """Send booking reminder email to user"""
    try:
        subject = f"Booking Reminder - {booking.room.name}"
        
        time_until_booking = booking.start_time - timezone.now()
        hours_until = int(time_until_booking.total_seconds() / 3600)
        
        message = f"""
Hello {booking.user.first_name}!

This is a reminder that you have a room booking in {hours_until} hours.

Booking Details:
Room: {booking.room.name} ({booking.room.room_number})
Date: {booking.start_time.strftime('%B %d, %Y')}
Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
Duration: {booking.duration} hours
Purpose: {booking.purpose}

Reminders:
- Please arrive on time
- Bring your student ID
- Contact us if you need to cancel or modify your booking

Thank you for using our Room Booking System!

This is an automated email. Please do not reply to this email.
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Booking reminder email sent to {booking.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send booking reminder email: {str(e)}")
        return False

def send_admin_notification_email(booking, action):
    """Send notification email to admin about booking actions"""
    try:
        subject = f"New Booking {action.title()} - {booking.room.name}"
        
        message = f"""
Admin Notification

A new booking {action} has occurred in the Room Booking System.

Booking Details:
User: {booking.user.first_name} {booking.user.last_name} ({booking.user.email})
Student ID: {booking.user.student_id}
Room: {booking.room.name} ({booking.room.room_number})
Date: {booking.start_time.strftime('%B %d, %Y')}
Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
Duration: {booking.duration} hours
Purpose: {booking.purpose}
Status: {booking.get_status_display()}
Action: {action.title()}
Timestamp: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}

Please review this booking in the admin dashboard if necessary.

Room Booking System - Admin Notification
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"Admin notification email sent for booking {action}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send admin notification email: {str(e)}")
        return False

def send_booking_reminder_batch():
    """Send reminder emails for bookings starting in 1 hour"""
    from .models import Booking
    
    # Get bookings starting in 1 hour
    one_hour_from_now = timezone.now() + timedelta(hours=1)
    upcoming_bookings = Booking.objects.filter(
        start_time__gte=one_hour_from_now - timedelta(minutes=30),
        start_time__lte=one_hour_from_now + timedelta(minutes=30),
        status='confirmed'
    )
    
    sent_count = 0
    for booking in upcoming_bookings:
        if send_booking_reminder_email(booking):
            sent_count += 1
    
    logger.info(f"Sent {sent_count} booking reminder emails")
    return sent_count

# Step 23: System Announcements
def send_announcement_email(announcement, users):
    """Send announcement email to specified users"""
    try:
        subject = f"System Announcement: {announcement.title}"
        
        message = f"""
System Announcement

{announcement.title}

{announcement.content}

Priority: {announcement.get_priority_display()}
Date: {announcement.created_at.strftime('%B %d, %Y')}

---
Room Booking System
This is an automated email. Please do not reply to this email.
        """
        
        recipient_list = [user.email for user in users if user.email]
        
        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            logger.info(f"Announcement email sent to {len(recipient_list)} users")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Failed to send announcement email: {str(e)}")
        return False