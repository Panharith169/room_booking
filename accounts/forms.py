from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form that matches your HTML frontend"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'id': 'firstName'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'id': 'lastName'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'id': 'email'
        })
    )
    
    student_id = forms.CharField(
        max_length=20,
        required=False,  # Make optional for flexibility
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Student ID (optional)',
            'id': 'studentId'
        })
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (optional)',
            'id': 'phoneNumber'
        })
    )
    
    faculty = forms.ChoiceField(
        choices=[('', 'Select Faculty')] + User.FACULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'faculty'
        })
    )
    
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department (optional)',
            'id': 'department'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'id': 'confirmPassword'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'student_id', 'phone_number', 'faculty', 'department')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if student_id and User.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("This student ID is already registered.")
        return student_id
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.student_id = self.cleaned_data.get('student_id') or f"USR{User.objects.count() + 1:06d}"
        user.phone_number = self.cleaned_data.get('phone_number') or "000-000-0000"
        user.faculty = self.cleaned_data.get('faculty', '')
        user.department = self.cleaned_data.get('department', '')
        
        if commit:
            user.save()
        return user

class CustomLoginForm(forms.Form):
    """Custom login form that matches your HTML frontend"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'id': 'username',  # Your HTML uses 'username' id
            'name': 'username'  # Your HTML uses 'username' name
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password'
        })
    )

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with your styling"""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current password',
            'id': 'currentPassword'
        })
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password',
            'id': 'newPassword'
        })
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'id': 'confirmPassword'
        })
    )

class UserUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'faculty', 'department']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
                'id': 'firstName'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
                'id': 'lastName'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'id': 'email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'id': 'phoneNumber'
            }),
            'faculty': forms.Select(attrs={
                'class': 'form-control',
                'id': 'faculty'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department',
                'id': 'department'
            }),
        }