from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from .models import User

class UserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            student_id='12345678',
            phone_number='0123456789',
            password='testpassword'
        )

    def test_login(self):
        login = self.client.login(email='test@example.com', password='testpassword')
        self.assertTrue(login)