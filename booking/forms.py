from django import forms
from django.core.exceptions import ValidationError
from .models import Room
from datetime import datetime, time

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
            'is_available': forms.CheckboxInput(attrs={
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
