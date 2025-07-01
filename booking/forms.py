# Enhanced bookings/forms.py - Adding Phase 5 forms to existing code

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Room, Booking, BookingRule
from django.db.models import Q

# ===== EXISTING FORMS FROM PHASE 4 =====

class RoomForm(forms.ModelForm):
    """Form for creating and editing rooms"""
    
    class Meta:
        model = Room
        fields = ['name', 'room_number', 'capacity', 'room_type', 'description', 
                 'equipment', 'availability_status', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room name'
            }),
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room number'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '500'
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter room description'
            }),
            'equipment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List available equipment (optional)'
            }),
            'availability_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_room_number(self):
        room_number = self.cleaned_data['room_number']
        
        # Check if room number already exists (excluding current instance for updates)
        query = Room.objects.filter(room_number=room_number)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise ValidationError('A room with this number already exists.')
        
        return room_number

    def clean_capacity(self):
        capacity = self.cleaned_data['capacity']
        if capacity < 1:
            raise ValidationError('Capacity must be at least 1.')
        return capacity


class RoomSearchForm(forms.Form):
    """Form for searching and filtering rooms"""
    
    ROOM_TYPE_CHOICES = [
        ('', 'All Types'),
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('conference', 'Conference Room'),
        ('auditorium', 'Auditorium'),
        ('library', 'Library Room'),
        ('study', 'Study Room'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, room number, or description...'
        })
    )
    
    room_type = forms.ChoiceField(
        choices=ROOM_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    min_capacity = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min capacity',
            'min': '1'
        })
    )
    
    max_capacity = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max capacity',
            'min': '1'
        })
    )
    
    availability_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Check availability for specific date'
    )
    
    start_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    
    end_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    
    available_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Show only available rooms'
    )

    def clean(self):
        cleaned_data = super().clean()
        min_capacity = cleaned_data.get('min_capacity')
        max_capacity = cleaned_data.get('max_capacity')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        availability_date = cleaned_data.get('availability_date')
        
        # Validate capacity range
        if min_capacity and max_capacity and min_capacity > max_capacity:
            raise ValidationError('Minimum capacity cannot be greater than maximum capacity.')
        
        # Validate time range
        if start_time and end_time and start_time >= end_time:
            raise ValidationError('Start time must be before end time.')
        
        # If checking availability by time, date is required
        if (start_time or end_time) and not availability_date:
            raise ValidationError('Date is required when checking time availability.')
        
        return cleaned_data

# ===== NEW PHASE 5 FORMS =====

class BookingForm(forms.ModelForm):
    """Form for creating and editing bookings"""
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        }),
        label='Booking Date'
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time', 
            'class': 'form-control',
            'step': '300'  # 5-minute intervals
        }),
        label='Start Time'
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time', 
            'class': 'form-control',
            'step': '300'  # 5-minute intervals
        }),
        label='End Time'
    )
    
    class Meta:
        model = Booking
        fields = ['room', 'start_date', 'start_time', 'end_time', 'purpose', 'additional_notes']
        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_room'
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Enter the purpose of your booking',
                'maxlength': 500
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Any additional notes or requirements (optional)',
                'maxlength': 300
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter only bookable rooms
        self.fields['room'].queryset = Room.objects.filter(
            is_active=True,
            availability_status='available'
        ).order_by('room_number')
        
        # Add empty option
        self.fields['room'].empty_label = "Select a room"
        
        # Set minimum date to today
        self.fields['start_date'].widget.attrs['min'] = timezone.now().date().isoformat()
        
        # Add help text
        self.fields['purpose'].help_text = "Please describe the purpose of your booking"
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        room = cleaned_data.get('room')
        
        if not all([start_date, start_time, end_time, room]):
            return cleaned_data
        
        # Combine date and time
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(start_date, end_time)
        
        # Make timezone aware
        start_datetime = timezone.make_aware(start_datetime)
        end_datetime = timezone.make_aware(end_datetime)
        
        # Basic time validation
        if end_datetime <= start_datetime:
            raise ValidationError("End time must be after start time.")
        
        # Check if booking is in the past
        if start_datetime <= timezone.now():
            raise ValidationError("Cannot book rooms in the past.")
        
        # Check if room is bookable
        if not room.is_bookable():
            raise ValidationError("This room is not available for booking.")
        
        # Check availability
        if not self.check_room_availability(room, start_datetime, end_datetime):
            raise ValidationError("Room is not available for the selected time slot.")
        
        # Validate against booking rules
        self.validate_booking_rules(start_datetime, end_datetime)
        
        cleaned_data['start_datetime'] = start_datetime
        cleaned_data['end_datetime'] = end_datetime
        
        return cleaned_data
    
    def check_room_availability(self, room, start_datetime, end_datetime):
        """Check if room is available for the given time slot"""
        conflicting_bookings = Booking.objects.filter(
            room=room,
            status__in=['confirmed', 'pending'],
            start_time__lt=end_datetime,
            end_time__gt=start_datetime
        )
        
        # Exclude current booking when editing
        if self.instance and self.instance.pk:
            conflicting_bookings = conflicting_bookings.exclude(pk=self.instance.pk)
        
        return not conflicting_bookings.exists()
    
    def validate_booking_rules(self, start_datetime, end_datetime):
        """Validate booking against system rules"""
        try:
            rules = BookingRule.objects.filter(is_active=True).first()
        except BookingRule.DoesNotExist:
            return  # No rules configured
        
        if not rules:
            return
        
        # Check maximum duration
        duration = end_datetime - start_datetime
        if duration > timedelta(hours=rules.max_duration_hours):
            raise ValidationError(f"Maximum booking duration is {rules.max_duration_hours} hours.")
        
        # Check advance booking limit
        advance_time = start_datetime - timezone.now()
        if advance_time > timedelta(days=rules.advance_booking_days):
            raise ValidationError(f"Cannot book more than {rules.advance_booking_days} days in advance.")
        
        # Check minimum advance time
        if hasattr(rules, 'min_advance_hours') and advance_time < timedelta(hours=rules.min_advance_hours):
            raise ValidationError(f"Must book at least {rules.min_advance_hours} hours in advance.")
        
        # Check booking time limits
        if hasattr(rules, 'booking_start_time') and rules.booking_start_time:
            if start_datetime.time() < rules.booking_start_time:
                raise ValidationError(f"Bookings cannot start before {rules.booking_start_time}.")
        
        if hasattr(rules, 'booking_end_time') and rules.booking_end_time:
            if end_datetime.time() > rules.booking_end_time:
                raise ValidationError(f"Bookings cannot end after {rules.booking_end_time}.")
        
        # Check user-specific limits
        if self.user:
            self.validate_user_limits(start_datetime, rules)
    
    def validate_user_limits(self, start_datetime, rules):
        """Validate user-specific booking limits"""
        # Check daily booking limits
        daily_bookings = Booking.objects.filter(
            user=self.user,
            start_time__date=start_datetime.date(),
            status__in=['confirmed', 'pending']
        )
        
        # Exclude current booking when editing
        if self.instance and self.instance.pk:
            daily_bookings = daily_bookings.exclude(pk=self.instance.pk)
        
        if daily_bookings.count() >= rules.max_daily_bookings:
            raise ValidationError(f"Daily booking limit of {rules.max_daily_bookings} reached.")
        
        # Check weekly booking limits
        week_start = start_datetime - timedelta(days=start_datetime.weekday())
        week_end = week_start + timedelta(days=6)
        
        weekly_bookings = Booking.objects.filter(
            user=self.user,
            start_time__date__gte=week_start.date(),
            start_time__date__lte=week_end.date(),
            status__in=['confirmed', 'pending']
        )
        
        # Exclude current booking when editing
        if self.instance and self.instance.pk:
            weekly_bookings = weekly_bookings.exclude(pk=self.instance.pk)
        
        if weekly_bookings.count() >= rules.max_weekly_bookings:
            raise ValidationError(f"Weekly booking limit of {rules.max_weekly_bookings} reached.")


class BookingSearchForm(forms.Form):
    """Form for searching and filtering bookings"""
    
    STATUS_CHOICES = [
        ('', 'All Statuses'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    DATE_RANGE_CHOICES = [
        ('', 'All Time'),
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('upcoming', 'Upcoming'),
        ('past', 'Past'),
        ('custom', 'Custom Range'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by room, purpose, or user...'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_range = forms.ChoiceField(
        choices=DATE_RANGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_active=True),
        required=False,
        empty_label="All Rooms",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        date_range = cleaned_data.get('date_range')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate custom date range
        if date_range == 'custom':
            if not start_date or not end_date:
                raise ValidationError('Start date and end date are required for custom range.')
            if start_date > end_date:
                raise ValidationError('Start date cannot be after end date.')
        
        return cleaned_data


class QuickBookingForm(forms.Form):
    """Simplified form for quick booking"""
    
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_active=True, availability_status='available'),
        empty_label="Select a room",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    duration = forms.ChoiceField(
        choices=[
            ('1', '1 hour'),
            ('2', '2 hours'),
            ('3', '3 hours'),
            ('4', '4 hours'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select booking duration'
    )
    
    start_time = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Available time slots for today'
    )
    
    purpose = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Brief purpose description'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Generate time slots for today
        self.fields['start_time'].choices = self.get_available_time_slots()
    
    def get_available_time_slots(self):
        """Generate available time slots for today"""
        time_slots = []
        current_time = timezone.now()
        
        # Start from next hour
        start_hour = (current_time.hour + 1) % 24
        
        for hour in range(start_hour, 22):  # Until 10 PM
            time_str = f"{hour:02d}:00"
            time_slots.append((time_str, time_str))
        
        return time_slots


class BookingRuleForm(forms.ModelForm):
    """Form for managing booking rules"""
    
    class Meta:
        model = BookingRule
        fields = [
            'name', 'max_duration_hours', 'max_daily_bookings', 
            'max_weekly_bookings', 'advance_booking_days',
            'min_advance_hours', 'booking_start_time', 
            'booking_end_time', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rule name'
            }),
            'max_duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.5',
                'step': '0.5'
            }),
            'max_daily_bookings': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'max_weekly_bookings': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'advance_booking_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'min_advance_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'booking_start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'booking_end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('booking_start_time')
        end_time = cleaned_data.get('booking_end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError('Booking start time must be before end time.')
        
        return cleaned_data


class BulkBookingForm(forms.Form):
    """Form for creating multiple bookings"""
    
    RECURRENCE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_active=True, availability_status='available'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    
    recurrence = forms.ChoiceField(
        choices=RECURRENCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    purpose = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError('Start date cannot be after end date.')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError('Start time must be before end time.')
        
        return cleaned_data