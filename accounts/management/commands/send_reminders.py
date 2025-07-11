# Add management command for sending reminder emails
# Create booking/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from booking.email_utils import send_booking_reminder_batch

class Command(BaseCommand):
    help = 'Send reminder emails for upcoming bookings'

    def handle(self, *args, **options):
        count = send_booking_reminder_batch()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {count} reminder emails')
        )
