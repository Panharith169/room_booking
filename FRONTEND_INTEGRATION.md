# Room Booking System Integration Documentation

## Overview
This document describes the integration between the `room_booking_system` (main Django project) and the `booking` folder (Django app) with the frontend templates.

## Project Structure
```
RoomBooking/
├── room_booking_system/          # Main Django project
│   ├── settings.py               # Project settings
│   ├── urls.py                   # Main URL configuration
│   └── wsgi.py                   # WSGI configuration
├── booking/                      # Booking Django app
│   ├── models.py                 # Room, Booking, BookingRule models
│   ├── views.py                  # Booking-related views
│   ├── urls.py                   # Booking app URLs
│   ├── forms.py                  # Booking forms
│   └── utils.py                  # Booking utilities
├── accounts/                     # User management app
│   ├── models.py                 # User model
│   ├── views.py                  # User views + booking integration
│   └── urls.py                   # Account URLs
├── templates/                    # Frontend templates
│   ├── UserPage/                 # User interface templates
│   │   ├── booking.html          # Main booking page
│   │   ├── booked.html           # User's bookings
│   │   ├── booking-detail.html   # Booking details
│   │   └── welcomeUser.html      # User dashboard
│   └── AdminPage/                # Admin interface templates
│       ├── adminHomePage.html    # Admin dashboard
│       ├── manageRooms.html      # Room management
│       └── allBookings.html      # All bookings view
└── static/                       # Static files
    ├── UserPage/
    │   ├── css/booking.css       # Booking page styles
    │   └── js/booking.js         # Booking page JavaScript
    └── AdminPage/
        └── css/                  # Admin styles
```

## Integration Points

### 1. URL Configuration
- **Main URLs** (`room_booking_system/urls.py`):
  - `/accounts/` -> accounts app
  - `/booking/` -> booking app
  - `/` -> redirects to login

- **Accounts URLs** (`accounts/urls.py`):
  - `/accounts/booking/` -> booking page (integrates with booking app)
  - `/accounts/booked/` -> user's bookings
  - `/accounts/ajax/check-availability/` -> AJAX availability check

- **Booking URLs** (`booking/urls.py`):
  - `/booking/rooms/` -> room list
  - `/booking/create/` -> create booking
  - `/booking/my-bookings/` -> user bookings

### 2. Model Integration
- **Room Model** (`booking/models.py`):
  - Stores room information (name, capacity, type, availability)
  - Used by both apps for room management

- **Booking Model** (`booking/models.py`):
  - Links users to rooms with time slots
  - Handles booking status (pending, confirmed, cancelled)

- **User Model** (`accounts/models.py`):
  - Custom user model with roles (Admin, User)
  - Integrated with booking system

### 3. View Integration
- **Accounts Views** (`accounts/views.py`):
  - `booking_view()` - Renders booking page with room data
  - `booked_view()` - Shows user's bookings
  - `create_booking_redirect()` - Redirects to booking app
  - AJAX endpoints for real-time availability

- **Booking Views** (`booking/views.py`):
  - `create_booking()` - Handles booking creation
  - `user_bookings()` - User's booking dashboard
  - `room_list()` - Available rooms
  - `check_availability()` - Availability checking

### 4. Frontend Integration
- **Templates**: All templates use the existing UserPage/AdminPage structure
- **JavaScript**: Enhanced with AJAX for real-time availability checking
- **CSS**: Styled to match the existing design system

## Key Features

### 1. Real-Time Availability Checking
- AJAX calls to check room availability as user types
- Visual feedback (green for available, red for unavailable)
- Prevents conflicting bookings

### 2. Role-Based Access
- Users can book rooms and view their bookings
- Admins can manage rooms and view all bookings
- Automatic redirection based on user role

### 3. Booking Management
- Create, view, modify, and cancel bookings
- Email notifications for booking confirmations
- Booking rules and restrictions

### 4. Room Management (Admin)
- Add, edit, and delete rooms
- Toggle room availability
- View booking statistics

## API Endpoints

### AJAX Endpoints
- `POST /accounts/ajax/check-availability/` - Check room availability
- `GET /accounts/ajax/get-rooms/` - Get rooms by building
- `GET /accounts/ajax/get-buildings/` - Get all buildings

### Booking Endpoints
- `POST /booking/create/` - Create new booking
- `GET /booking/my-bookings/` - User's bookings
- `POST /booking/<id>/cancel/` - Cancel booking
- `GET /booking/rooms/` - Available rooms

## Configuration

### Settings (`room_booking_system/settings.py`)
```python
INSTALLED_APPS = [
    # ...
    'accounts.apps.AccountsConfig',
    'booking',
]

TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],
        'OPTIONS': {
            'context_processors': [
                # ...
                'booking.context_processors.room_types',
            ],
        },
    },
]

AUTH_USER_MODEL = 'accounts.User'
```

### Database Models
- Ensure migrations are run for both apps:
  ```bash
  python manage.py makemigrations accounts
  python manage.py makemigrations booking
  python manage.py migrate
  ```

## Usage

### For Users
1. Login to the system
2. Navigate to "Booking" page
3. Select building and room
4. Choose date and time
5. Submit booking request
6. View bookings in "Booked" section

### For Admins
1. Login with admin credentials
2. Access admin dashboard
3. Manage rooms in "Manage Rooms"
4. View all bookings in "All Bookings"
5. Approve/reject booking requests

## Error Handling
- Graceful degradation if booking models are not available
- Fallback data for development/testing
- Proper error messages for users
- AJAX error handling with user feedback

## Security
- CSRF protection on all forms
- User authentication required
- Role-based access control
- Input validation and sanitization

## Future Enhancements
- Calendar view for bookings
- Advanced search and filtering
- Booking conflict resolution
- Email notifications
- Booking analytics and reporting

## Troubleshooting

### Common Issues
1. **Templates not found**: Check TEMPLATES setting in settings.py
2. **AJAX not working**: Verify CSRF token is included in requests
3. **Models not accessible**: Ensure apps are in INSTALLED_APPS
4. **Static files not loading**: Run `python manage.py collectstatic`

### Debug Mode
- Set `DEBUG = True` in settings.py for development
- Check Django logs for detailed error messages
- Use browser developer tools for frontend debugging

## Deployment
- Set `DEBUG = False` for production
- Configure proper database settings
- Set up static files serving
- Configure email backend for notifications
- Set up proper logging
