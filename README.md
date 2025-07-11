# RUPP Room Booking System

A comprehensive Django-based room booking system for Royal University of Phnom Penh (RUPP).

## Features

### User Features
- **User Registration & Authentication**: Students can register and log in
- **Room Browsing**: View available rooms with details and facilities
- **Room Booking**: Book rooms for specific dates and times
- **Booking Management**: View, modify, and cancel existing bookings
- **Profile Management**: Update personal information and settings
- **Responsive Design**: Works on desktop and mobile devices

### Admin Features
- **Admin Dashboard**: Overview of system statistics
- **Room Management**: Add, edit, and delete rooms
- **Booking Management**: Approve, reject, or cancel bookings
- **User Management**: Promote users to admin status
- **System Settings**: Configure system preferences

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: MySQL 8.0
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Django built-in auth with custom User model
- **Icons**: Font Awesome 6

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package installer)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RoomBooking
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database**
   - Create a MySQL database named `room_booking`
   - Update database settings in `room_booking_system/settings.py`:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'room_booking',
             'USER': 'your_mysql_username',
             'PASSWORD': 'your_mysql_password',
             'HOST': 'localhost',
             'PORT': '3306',
         }
     }
     ```

4. **Run the setup script**
   ```bash
   python setup_and_run.py
   ```

### Manual Setup

If you prefer manual setup:

1. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create admin account**
   ```bash
   python manage.py setup_initial_data
   ```

3. **Setup sample rooms**
   ```bash
   python manage.py setup_rooms
   ```

4. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

## Default Accounts

After setup, you can log in with these default accounts:

### Admin Account
- **Email**: admin@rupp.edu.kh
- **Password**: admin123
- **Access**: Full administrative privileges

### Test User Account
- **Email**: student@rupp.edu.kh
- **Password**: student123
- **Access**: Standard user features

## Usage

### For Students

1. **Registration**
   - Visit the registration page
   - Fill in your details (name, email, student ID, faculty, etc.)
   - Submit the form to create your account

2. **Room Booking**
   - Log in to your account
   - Browse available rooms
   - Select a room and choose your preferred date/time
   - Submit booking request (requires admin approval)

3. **Managing Bookings**
   - View all your bookings in the "Booked" section
   - Check booking status (Pending, Approved, Rejected)
   - Cancel bookings if needed

### For Administrators

1. **Dashboard**
   - Overview of system statistics
   - Quick access to admin functions

2. **Room Management**
   - Add new rooms with details and facilities
   - Edit existing room information
   - Delete rooms that are no longer available

3. **Booking Management**
   - Review pending booking requests
   - Approve or reject bookings
   - Cancel approved bookings if necessary

4. **User Management**
   - Promote regular users to admin status
   - View all registered users

## Project Structure

```
RoomBooking/
├── accounts/                 # User authentication and management
│   ├── models.py            # Custom User model
│   ├── views.py             # Authentication and user views
│   ├── forms.py             # User registration and profile forms
│   └── urls.py              # URL patterns for accounts
├── booking/                  # Room and booking management
│   ├── models.py            # Room and Booking models
│   ├── views.py             # Booking-related views
│   └── admin.py             # Admin interface configuration
├── templates/               # HTML templates
│   ├── AdminPage/           # Admin interface templates
│   ├── UserPage/            # User interface templates
│   └── SignIn-RegisterPage/ # Authentication templates
├── static/                  # Static files (CSS, JS, images)
│   ├── AdminPage/
│   ├── UserPage/
│   └── public/
├── media/                   # User uploaded files
└── room_booking_system/     # Django project settings
    ├── settings.py          # Project configuration
    ├── urls.py              # Main URL configuration
    └── wsgi.py              # WSGI configuration
```

## Key Features Explained

### User Role Management
- **Groups**: Users are automatically assigned to 'User' or 'Admin' groups
- **Permissions**: Role-based access control for different features
- **Role Switching**: Admins can promote users to admin status

### Room Management
- **Room Types**: Support for various room types (classroom, lab, conference, etc.)
- **Capacity Management**: Track room capacity and availability
- **Equipment Tracking**: List available equipment in each room

### Booking System
- **Status Tracking**: Bookings have status (pending, approved, rejected, cancelled)
- **Time Validation**: Prevent double bookings and conflicts
- **Admin Approval**: Bookings require admin approval before confirmation

### Security Features
- **CSRF Protection**: All forms protected against CSRF attacks
- **User Authentication**: Required for all booking operations
- **Permission Checks**: Role-based access to admin functions

## Customization

### Adding New Room Types
Edit `booking/models.py` and add new choices to `ROOM_TYPES`:
```python
ROOM_TYPES = [
    ('classroom', 'Classroom'),
    ('lab', 'Laboratory'),
    ('conference', 'Conference Room'),
    ('your_new_type', 'Your New Type'),  # Add this line
]
```

### Modifying Email Settings
Update email configuration in `settings.py` for production:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify database credentials in settings.py
   - Ensure database 'room_booking' exists

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_URL and STATICFILES_DIRS in settings.py

3. **Permission Errors**
   - Ensure user has correct group assignment
   - Check if admin account has proper permissions

### Getting Help

If you encounter issues:
1. Check the Django development server console for error messages
2. Review the error logs for detailed information
3. Ensure all dependencies are installed correctly

## Development

### Setting Up Development Environment

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   python manage.py test
   ```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## License

This project is developed for educational purposes at Royal University of Phnom Penh (RUPP).

## Contact

For support or questions, contact the development team:
- **Team**: DSE TEAM
- **University**: Royal University of Phnom Penh
- **Department**: Data Science and Engineering

---

**© 2025 Royal University of Phnom Penh (RUPP)**
