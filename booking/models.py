from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, datetime, time

# class CustomUser(AbstractUser):
#     """Extended User model with additional fields"""
    
#     USER_TYPES = [
#         ('student', 'Student'),
#         ('faculty', 'Faculty'),
#         ('staff', 'Staff'),
#         ('admin', 'Administrator'),
#     ]
    
#     # Additional fields
#     user_type = models.CharField(
#         max_length=20,
#         choices=USER_TYPES,
#         default='student',
#         help_text='Type of user'
#     )
    
#     student_id = models.CharField(
#         max_length=20,
#         blank=True,
#         null=True,
#         unique=True,
#         help_text='Student ID number (for students)'
#     )
    
#     employee_id = models.CharField(
#         max_length=20,
#         blank=True,
#         null=True,
#         unique=True,
#         help_text='Employee ID number (for faculty/staff)'
#     )
    
#     phone_number = models.CharField(
#         max_length=15,
#         blank=True,
#         validators=[
#             RegexValidator(
#                 regex=r'^\+?1?\d{9,15}$',
#                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
#             )
#         ],
#         help_text='Contact phone number'
#     )
    
#     department = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text='Department or faculty'
#     )
    
#     is_approved = models.BooleanField(
#         default=False,
#         help_text='Whether the user account is approved for booking'
#     )
    
#     max_concurrent_bookings = models.PositiveIntegerField(
#         default=2,
#         help_text='Maximum number of concurrent active bookings allowed'
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'custom_users'
#         verbose_name = 'User'
#         verbose_name_plural = 'Users'
#         indexes = [
#             models.Index(fields=['user_type']),
#             models.Index(fields=['is_approved']),
#             models.Index(fields=['student_id']),
#             models.Index(fields=['employee_id']),
#         ]
    
#     def clean(self):
#         """Custom validation"""
#         # Validate student_id for students
#         if self.user_type == 'student' and not self.student_id:
#             raise ValidationError({'student_id': 'Student ID is required for students.'})
        
#         # Validate employee_id for faculty/staff
#         if self.user_type in ['faculty', 'staff'] and not self.employee_id:
#             raise ValidationError({'employee_id': 'Employee ID is required for faculty and staff.'})
        
#         # Clear irrelevant IDs
#         if self.user_type != 'student':
#             self.student_id = None
#         if self.user_type not in ['faculty', 'staff']:
#             self.employee_id = None
    
#     def save(self, *args, **kwargs):
#         self.clean()
#         super().save(*args, **kwargs)
    
#     def get_display_name(self):
#         """Return display name for the user"""
#         if self.get_full_name():
#             return self.get_full_name()
#         return self.username
    
#     def get_identifier(self):
#         """Return the appropriate ID for the user type"""
#         if self.user_type == 'student' and self.student_id:
#             return self.student_id
#         elif self.user_type in ['faculty', 'staff'] and self.employee_id:
#             return self.employee_id
#         return self.username
    
#     def can_make_booking(self):
#         """Check if user can make bookings"""
#         return self.is_active and self.is_approved
    
#     def __str__(self):
#         name = self.get_display_name()
#         identifier = self.get_identifier()
#         if identifier != name:
#             return f"{name} ({identifier})"
#         return name


class Room(models.Model):
    """Room model for managing bookable rooms"""
    
    ROOM_TYPES = [
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('conference', 'Conference Room'),
        ('auditorium', 'Auditorium'),
        ('library', 'Library Room'),
        ('study', 'Study Room'),
        ('other', 'Other'),
    ]
    
    AVAILABILITY_STATUS = [
        ('available', 'Available'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('unavailable', 'Unavailable'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text='Room name or identifier'
    )
    
    room_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique room number'
    )
    
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text='Maximum number of people the room can accommodate'
    )
    
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPES,
        default='classroom',
        help_text='Type of room'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Detailed description of the room'
    )
    
    equipment = models.TextField(
        blank=True,
        help_text='Available equipment (projector, whiteboard, computers, etc.)'
    )
    
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default='available',
        help_text='Current availability status'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the room is active and bookable'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rooms'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['room_number', 'name']
        indexes = [
            models.Index(fields=['room_type']),
            models.Index(fields=['availability_status']),
            models.Index(fields=['is_active']),
        ]
    
    def clean(self):
        """Custom validation for room"""
        if self.capacity < 1:
            raise ValidationError({'capacity': 'Capacity must be at least 1.'})
        
        if self.room_number:
            self.room_number = self.room_number.upper().strip()
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def is_bookable(self):
        """Check if room is available for booking"""
        return self.is_active and self.availability_status == 'available'
    
    def get_absolute_url(self):
        """Get the URL for this room's detail page"""
        from django.urls import reverse
        return reverse('booking:room_detail', kwargs={'room_id': self.id})
    
    def is_available_at(self, start_datetime, end_datetime):
        """Check if room is available at given datetime range"""
        if not self.is_bookable():
            return False
        
        conflicts = self.bookings.filter(
            start_time__lt=end_datetime,
            end_time__gt=start_datetime,
            status__in=['confirmed', 'pending']
        )
        
        return not conflicts.exists()
    
    def get_next_booking(self):
        """Get the next upcoming booking for this room"""
        return self.bookings.filter(
            start_time__gt=timezone.now(),
            status__in=['confirmed', 'pending']
        ).order_by('start_time').first()
    
    def get_current_booking(self):
        """Get current active booking if any"""
        now = timezone.now()
        return self.bookings.filter(
            start_time__lte=now,
            end_time__gte=now,
            status='confirmed'
        ).first()
    
    def __str__(self):
        return f"{self.name} ({self.room_number})"


class BookingRule(models.Model):
    """Model for defining booking rules and constraints"""
    
    name = models.CharField(
        max_length=100,
        help_text='Rule name'
    )
    
    max_duration_hours = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(24)],
        help_text='Maximum booking duration in hours'
    )
    
    max_daily_bookings = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Maximum bookings per user per day'
    )
    
    max_weekly_bookings = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text='Maximum bookings per user per week'
    )
    
    advance_booking_days = models.PositiveIntegerField(
        default=14,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text='How many days in advance users can book'
    )
    
    min_advance_hours = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(168)],
        help_text='Minimum hours in advance required for booking'
    )
    
    booking_start_time = models.TimeField(
        default=time(7, 0),
        help_text='Earliest time rooms can be booked'
    )
    
    booking_end_time = models.TimeField(
        default=time(22, 0),
        help_text='Latest time rooms can be booked'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this rule set is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'booking_rules'
        verbose_name = 'Booking Rule'
        verbose_name_plural = 'Booking Rules'
        ordering = ['-is_active', 'name']
    
    def clean(self):
        """Custom validation for booking rules"""
        if self.booking_start_time >= self.booking_end_time:
            raise ValidationError({
                'booking_end_time': 'End time must be after start time.'
            })
        
        if self.max_duration_hours > 24:
            raise ValidationError({
                'max_duration_hours': 'Maximum duration cannot exceed 24 hours.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"


# Custom managers for efficient queries
class BookingManager(models.Manager):
    """Custom manager for Booking model"""
    
    def active_bookings(self):
        """Return active bookings"""
        return self.filter(
            status__in=['pending', 'confirmed'],
            end_time__gt=timezone.now()
        )
    
    def user_bookings_today(self, user):
        """Return user's bookings for today"""
        today = timezone.now().date()
        return self.filter(
            user=user,
            start_time__date=today,
            status__in=['pending', 'confirmed']
        )
    
    def user_bookings_this_week(self, user):
        """Return user's bookings for this week"""
        week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
        week_end = week_start + timedelta(days=6)
        return self.filter(
            user=user,
            start_time__date__range=[week_start, week_end],
            status__in=['pending', 'confirmed']
        )


class Booking(models.Model):
    """Booking model for room reservations"""
    def can_be_cancelled(self):
        """Check if booking can be cancelled based on time restrictions"""
        try:
            rules = BookingRule.objects.get(id=1)
            time_until_start = self.start_time - timezone.now()
            return time_until_start >= timedelta(hours=rules.min_cancellation_hours)
        except BookingRule.DoesNotExist:
            return True  # Allow cancellation if no rules
    
    def can_be_modified(self):
        """Check if booking can be modified"""
        return self.status == 'pending' and self.can_be_cancelled()
    
    def get_cancellation_deadline(self):
        """Get the deadline for cancellation"""
        try:
            rules = BookingRule.objects.get(id=1)
            return self.start_time - timedelta(hours=rules.min_cancellation_hours)
        except BookingRule.DoesNotExist:
            return self.start_time
    
    def clean(self):
        """Model validation"""
        super().clean()
        
        # Validate end time after start time
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        
        # Check for booking conflicts
        conflicting_bookings = Booking.objects.filter(
            room=self.room,
            status__in=['confirmed', 'pending'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if conflicting_bookings.exists():
            raise ValidationError("This time slot conflicts with an existing booking.")

    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='User who made the booking'
    )
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='Room being booked'
    )
    
    start_time = models.DateTimeField(
        help_text='Booking start date and time'
    )
    
    end_time = models.DateTimeField(
        help_text='Booking end date and time'
    )
    
    purpose = models.CharField(
        max_length=200,
        help_text='Purpose of the booking'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current booking status'
    )
    
    additional_notes = models.TextField(
        blank=True,
        help_text='Additional notes or requirements'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    
    # Custom manager
    objects = BookingManager()
    
    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['room', 'start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['start_time', 'end_time']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_time__lt=models.F('end_time')),
                name='start_time_before_end_time'
            )
        ]
    
    def clean(self):
        """Custom validation for booking"""
        if not self.start_time or not self.end_time:
            return
        
        # Check if start time is before end time
        if self.start_time >= self.end_time:
            raise ValidationError({
                'end_time': 'End time must be after start time.'
            })
        
        # Check if booking is in the past
        if self.start_time < timezone.now():
            raise ValidationError({
                'start_time': 'Cannot book rooms in the past.'
            })
        
        # Check booking duration
        duration = self.end_time - self.start_time
        max_duration = timedelta(hours=8)  # Default max duration
        
        try:
            rule = BookingRule.objects.filter(is_active=True).first()
            if rule:
                max_duration = timedelta(hours=rule.max_duration_hours)
        except:
            pass
        
        if duration > max_duration:
            raise ValidationError({
                'end_time': f'Booking duration cannot exceed {max_duration.total_seconds()/3600} hours.'
            })
        
        # Check for overlapping bookings (exclude current booking if updating)
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            status__in=['pending', 'confirmed'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        
        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)
        
        if overlapping_bookings.exists():
            raise ValidationError({
                'start_time': 'This room is already booked for the selected time period.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def duration(self):
        """Return booking duration as timedelta"""
        return self.end_time - self.start_time
    
    @property
    def duration_hours(self):
        """Return booking duration in hours"""
        return self.duration.total_seconds() / 3600
    
    def is_active(self):
        """Check if booking is currently active"""
        now = timezone.now()
        return (self.start_time <= now <= self.end_time and 
                self.status == 'confirmed')
    
    def can_cancel(self):
        """Check if booking can be cancelled"""
        return (self.status in ['pending', 'confirmed'] and 
                self.start_time > timezone.now())
    
    def __str__(self):
        return f"{self.room.name} - {self.user.get_full_name()} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"


class Announcement(models.Model):
    """Model for admin announcements"""
    
    ANNOUNCEMENT_TYPES = [
        ('general', 'General'),
        ('maintenance', 'Maintenance'),
        ('policy', 'Policy Update'),
        ('emergency', 'Emergency'),
        ('event', 'Event'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text='Announcement title'
    )
    
    content = models.TextField(
        help_text='Announcement content'
    )
    
    announcement_type = models.CharField(
        max_length=20,
        choices=ANNOUNCEMENT_TYPES,
        default='general',
        help_text='Type of announcement'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='normal',
        help_text='Priority level'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the announcement is active'
    )
    
    show_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Show announcement until this date (leave blank for indefinite)'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements',
        help_text='Admin who created the announcement'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'announcements'
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'show_until']),
            models.Index(fields=['announcement_type']),
            models.Index(fields=['priority']),
        ]
    
    def clean(self):
        """Custom validation for announcement"""
        if self.show_until and self.show_until < timezone.now():
            raise ValidationError({
                'show_until': 'Show until date cannot be in the past.'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def is_visible(self):
        """Check if announcement should be visible"""
        if not self.is_active:
            return False
        
        if self.show_until and timezone.now() > self.show_until:
            return False
        
        return True
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"


# =============================================
# Utility functions and validation
# =============================================

def validate_booking_time_slot(start_time, end_time):
    """Utility function to validate booking time slots"""
    try:
        rule = BookingRule.objects.filter(is_active=True).first()
        if not rule:
            return True  # No rules defined, allow booking
        
        # Check if booking is within allowed hours
        booking_start_time = start_time.time()
        booking_end_time = end_time.time()
        
        if (booking_start_time < rule.booking_start_time or 
            booking_end_time > rule.booking_end_time):
            raise ValidationError(
                f'Bookings are only allowed between {rule.booking_start_time} and {rule.booking_end_time}'
            )
        
        # Check advance booking limit
        advance_limit = timezone.now() + timedelta(days=rule.advance_booking_days)
        if start_time > advance_limit:
            raise ValidationError(
                f'Cannot book more than {rule.advance_booking_days} days in advance'
            )
        
        # Check minimum advance time
        min_advance_time = timezone.now() + timedelta(hours=rule.min_advance_hours)
        if start_time < min_advance_time:
            raise ValidationError(
                f'Must book at least {rule.min_advance_hours} hours in advance'
            )
        
        return True
        
    except Exception as e:
        raise ValidationError(f'Booking validation error: {str(e)}')


# Migration commands to run:
"""
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Test database connection
python manage.py shell
"""