"""
Admin Configuration Script
This script ensures all admin functionality is properly configured
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking_system.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import User

def setup_admin_groups_and_permissions():
    """Setup admin groups and permissions"""
    print("Setting up admin groups and permissions...")
    
    # Create groups
    admin_group, created = Group.objects.get_or_create(name='Admin')
    user_group, created = Group.objects.get_or_create(name='User')
    
    # Get content types
    user_content_type = ContentType.objects.get_for_model(User)
    
    # Create permissions for admin group
    permissions = [
        ('can_manage_users', 'Can manage users'),
        ('can_manage_rooms', 'Can manage rooms'),
        ('can_manage_bookings', 'Can manage bookings'),
        ('can_view_admin_dashboard', 'Can view admin dashboard'),
        ('can_change_user_roles', 'Can change user roles'),
        ('can_toggle_user_status', 'Can toggle user status'),
    ]
    
    for codename, name in permissions:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=user_content_type,
        )
        admin_group.permissions.add(permission)
    
    print(f"✓ Admin group configured with {len(permissions)} permissions")
    print(f"✓ User group created")
    
    return admin_group, user_group

def create_superuser_admin():
    """Create a superuser admin account"""
    print("\nCreating superuser admin account...")
    
    try:
        from accounts.views import assign_user_role
        
        # Create superuser
        email = "admin@rupp.edu.kh"
        if not User.objects.filter(email=email).exists():
            admin_user = User.objects.create_user(
                email=email,
                password='admin123',
                first_name='System',
                last_name='Administrator',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            
            # Assign admin role
            assign_user_role(admin_user, 'Admin')
            print(f"✓ Created superuser admin: {email}")
        else:
            admin_user = User.objects.get(email=email)
            assign_user_role(admin_user, 'Admin')
            print(f"✓ Superuser admin already exists: {email}")
            
        return admin_user
        
    except Exception as e:
        print(f"✗ Error creating superuser: {e}")
        return None

def create_test_users():
    """Create test users for demonstration"""
    print("\nCreating test users...")
    
    try:
        from accounts.views import assign_user_role
        
        # Test regular users
        test_users = [
            {
                'email': 'student1@rupp.edu.kh',
                'first_name': 'John',
                'last_name': 'Doe',
                'faculty': 'Engineering',
                'department': 'Computer Science',
                'role': 'User'
            },
            {
                'email': 'student2@rupp.edu.kh',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'faculty': 'Business',
                'department': 'Management',
                'role': 'User'
            },
            {
                'email': 'staff@rupp.edu.kh',
                'first_name': 'Staff',
                'last_name': 'Member',
                'faculty': 'Administration',
                'department': 'IT',
                'role': 'Admin'
            }
        ]
        
        for user_data in test_users:
            email = user_data['email']
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password='test123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    faculty=user_data.get('faculty', ''),
                    department=user_data.get('department', ''),
                    is_active=True
                )
                
                # Assign role
                assign_user_role(user, user_data['role'])
                print(f"✓ Created {user_data['role'].lower()}: {email}")
            else:
                print(f"✓ User already exists: {email}")
                
    except Exception as e:
        print(f"✗ Error creating test users: {e}")

def setup_room_data():
    """Setup sample room data"""
    print("\nSetting up sample room data...")
    
    try:
        from booking.models import Room
        
        sample_rooms = [
            {
                'name': 'Conference Room A',
                'room_number': 'A-101',
                'room_type': 'conference',
                'capacity': 20,
                'description': 'Large conference room with projector',
                'equipment': 'Projector, Whiteboard, AC',
                'is_available': True
            },
            {
                'name': 'Meeting Room B',
                'room_number': 'B-205',
                'room_type': 'meeting',
                'capacity': 10,
                'description': 'Small meeting room for team discussions',
                'equipment': 'TV Screen, Whiteboard',
                'is_available': True
            },
            {
                'name': 'Computer Lab',
                'room_number': 'C-301',
                'room_type': 'lab',
                'capacity': 30,
                'description': 'Computer lab with 30 workstations',
                'equipment': 'Computers, Projector, AC',
                'is_available': True
            },
            {
                'name': 'Auditorium',
                'room_number': 'D-001',
                'room_type': 'auditorium',
                'capacity': 200,
                'description': 'Main auditorium for large events',
                'equipment': 'Sound System, Projector, Stage',
                'is_available': False
            }
        ]
        
        for room_data in sample_rooms:
            room_number = room_data['room_number']
            if not Room.objects.filter(room_number=room_number).exists():
                Room.objects.create(**room_data)
                print(f"✓ Created room: {room_data['name']} ({room_number})")
            else:
                print(f"✓ Room already exists: {room_number}")
                
    except ImportError:
        print("✗ Room model not available. Skipping room setup.")
    except Exception as e:
        print(f"✗ Error setting up rooms: {e}")

def verify_admin_functionality():
    """Verify admin functionality is working"""
    print("\nVerifying admin functionality...")
    
    try:
        # Check admin views
        from accounts.views import (
            admin_dashboard_view,
            manage_users_view,
            ajax_change_user_role,
            ajax_toggle_user_status
        )
        print("✓ Admin views imported successfully")
        
        # Check URL patterns
        from accounts.urls import urlpatterns
        admin_urls = [url for url in urlpatterns if 'admin' in str(url.pattern)]
        ajax_urls = [url for url in urlpatterns if 'ajax' in str(url.pattern)]
        
        print(f"✓ Found {len(admin_urls)} admin URLs")
        print(f"✓ Found {len(ajax_urls)} AJAX URLs")
        
        # Check user counts
        total_users = User.objects.count()
        admin_users = User.objects.filter(groups__name='Admin').count()
        regular_users = User.objects.filter(groups__name='User').count()
        
        print(f"✓ Total users: {total_users}")
        print(f"✓ Admin users: {admin_users}")
        print(f"✓ Regular users: {regular_users}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error verifying admin functionality: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Admin Backend Configuration")
    print("=" * 50)
    
    # Step 1: Setup groups and permissions
    admin_group, user_group = setup_admin_groups_and_permissions()
    
    # Step 2: Create superuser admin
    admin_user = create_superuser_admin()
    
    # Step 3: Create test users
    create_test_users()
    
    # Step 4: Setup sample room data
    setup_room_data()
    
    # Step 5: Verify functionality
    if verify_admin_functionality():
        print("\n" + "=" * 50)
        print("🎉 Admin backend configuration completed successfully!")
        print("\nAdmin Login Credentials:")
        print("Email: admin@rupp.edu.kh")
        print("Password: admin123")
        print("\nTest User Credentials:")
        print("Email: student1@rupp.edu.kh")
        print("Password: test123")
        print("\nNext Steps:")
        print("1. Run: python manage.py runserver")
        print("2. Go to: http://localhost:8000/accounts/login/")
        print("3. Login with admin credentials")
        print("4. Navigate to admin dashboard")
        print("5. Test all admin functions")
        
    else:
        print("\n" + "=" * 50)
        print("❌ Admin backend configuration failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
