# tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class SignupTests(TestCase):
    def test_signup(self):
        # Test a valid registration request
        response = self.client.post(reverse('core:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword'
        })
        self.assertRedirects(response, reverse('core:login'))
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)

    def test_signup_with_invalid_email(self):
        # Test invalid email formats
        response = self.client.post(reverse('core:signup'), {
            'username': 'newuser2',
            'email': 'invalid-email',
            'first_name': 'New2',
            'last_name': 'User2',
            'password': 'newpassword2'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='newuser2').count(), 0)

    def test_signup_with_existing_username(self):
        # Test for duplicate user names
        User.objects.create_user('existinguser', 'existing@example.com', 'existingpassword')
        response = self.client.post(reverse('core:signup'), {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

