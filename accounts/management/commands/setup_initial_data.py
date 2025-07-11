from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup initial admin account and groups'

    def handle(self, *args, **options):
        try:
            # Create groups
            user_group, created = Group.objects.get_or_create(name='User')
            if created:
                self.stdout.write(self.style.SUCCESS('Created User group'))
            
            admin_group, created = Group.objects.get_or_create(name='Admin')
            if created:
                self.stdout.write(self.style.SUCCESS('Created Admin group'))
            
            # Create admin account
            admin_email = 'admin@rupp.edu.kh'
            if not User.objects.filter(email=admin_email).exists():
                admin_user = User.objects.create_user(
                    email=admin_email,
                    password='admin123',
                    first_name='System',
                    last_name='Administrator',
                    student_id='ADM001',
                    phone_number='+855-12-345-678',
                    faculty='engineering',
                    department='IT Department'
                )
                admin_user.groups.add(admin_group)
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.is_admin = True
                admin_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created admin account: {admin_email} / password: admin123'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Admin account {admin_email} already exists')
                )
            
            # Create test user
            user_email = 'student@rupp.edu.kh'
            if not User.objects.filter(email=user_email).exists():
                test_user = User.objects.create_user(
                    email=user_email,
                    password='student123',
                    first_name='Test',
                    last_name='Student',
                    student_id='STU001',
                    phone_number='+855-98-765-432',
                    faculty='science',
                    department='Computer Science'
                )
                test_user.groups.add(user_group)
                test_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created test user: {user_email} / password: student123'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Test user {user_email} already exists')
                )
            
            # Create additional test users
            test_users = [
                {
                    'email': 'john.doe@rupp.edu.kh',
                    'password': 'student123',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'student_id': 'STU002',
                    'phone_number': '+855-77-123-456',
                    'faculty': 'engineering',
                    'department': 'Computer Engineering'
                },
                {
                    'email': 'jane.smith@rupp.edu.kh',
                    'password': 'student123',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'student_id': 'STU003',
                    'phone_number': '+855-88-654-321',
                    'faculty': 'business',
                    'department': 'Business Administration'
                }
            ]
            
            for user_data in test_users:
                if not User.objects.filter(email=user_data['email']).exists():
                    new_user = User.objects.create_user(**user_data)
                    new_user.groups.add(user_group)
                    new_user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Created test user: {user_data["email"]}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Setup completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during setup: {str(e)}')
            )
