from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'student_id', 'phone_number', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Disable bulk actions but keep individual actions
    actions = []  # Remove all bulk actions
    
    fieldsets = (
    (None, {'fields': ('email', 'password')}),
    ('Personal Info', {'fields': ('first_name', 'last_name', 'student_id', 'phone_number')}),
    ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'student_id', 'phone_number', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'student_id', 'phone_number')
    ordering = ('-created_at',)

admin.site.register(User, CustomUserAdmin)