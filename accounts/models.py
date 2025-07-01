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
            regex=r'^\d{8,12}$',
            message='Student ID must be 8-12 digits'
        )],
        help_text='8-12 digit student identification number'
    )

    phone_number = models.CharField(
        'Phone Number',
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be 9-15 digits'
        )],
        help_text='Format: +999999999'
    )

    is_staff = models.BooleanField(
        'Staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.'
    )

    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['student_id', 'phone_number']

    objects = UserManager()

    class Meta:
        db_table = 'accounts_user'
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} ({self.student_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name