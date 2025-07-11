from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, student_id, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, student_id=student_id, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, student_id, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, student_id, phone_number, password, **extra_fields)

class User(AbstractUser):
    username = None

    email = models.EmailField(
        'Email Address',
        unique=True,
        help_text='Required. Must be a valid email address.'
    )

    student_id = models.CharField(
        'Student ID',
        max_length=20,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]{6,20}$',  # Made more flexible for your frontend
            message='Student ID must be 6-20 characters (letters and numbers)'
        )],
        help_text='6-20 character student identification',
        blank=True  # Allow blank for admin accounts
    )

    phone_number = models.CharField(
        'Phone Number',
        max_length=20,  # Increased for international formats
        validators=[RegexValidator(
            regex=r'^\+?[\d\s\-\(\)]{9,20}$',  # More flexible format
            message='Phone number must be valid format'
        )],
        help_text='Format: +999999999 or 999-999-9999',
        blank=True
    )

    is_admin = models.BooleanField(
        'Admin status',
        default=False,
        help_text='Designates administrative privileges (different from staff status)'
    )

    FACULTY_CHOICES = [
        ('science', 'Faculty of Science'),
        ('engineering', 'Faculty of Engineering'),
        ('social', 'Faculty of Social Sciences'),
        ('business', 'Faculty of Business'),
        ('education', 'Faculty of Education'),
        ('arts', 'Faculty of Arts'),
        ('law', 'Faculty of Law'),
        ('medicine', 'Faculty of Medicine'),
        ('agriculture', 'Faculty of Agriculture'),
    ]
    
    faculty = models.CharField(
        'Faculty',
        max_length=50,
        choices=FACULTY_CHOICES,
        blank=True
    )
    
    department = models.CharField(
        'Department',
        max_length=100,  # Increased for longer department names
        blank=True
    )

    is_staff = models.BooleanField(
        'Staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.'
    )

    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Made more flexible

    objects = UserManager()

    class Meta:
        db_table = 'accounts_user'
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name
    
    def get_student_display_id(self):
        """Return student ID or generate one if missing"""
        if self.student_id:
            return self.student_id
        return f"USR{self.id:06d}"
    
    def get_phone_display(self):
        """Return phone number or default"""
        return self.phone_number or "000-000-0000"
    
    def is_regular_user(self):
        """Check if user is a regular user (not admin)"""
        return not self.is_admin and not self.is_staff
    
    def is_admin_user(self):
        """Check if user is admin"""
        return self.is_admin or self.is_staff or self.is_superuser