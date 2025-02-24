from django.test import TestCase
from django.urls import reverse

from django.test import TestCase
from django.urls import reverse

class LoginTests(TestCase):
    def test_login(self):
        # Use the appropriate user name and password in the test
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        # Register the test, using the correct field name
        response = self.client.post(reverse('core:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword',
        })
        self.assertEqual(response.status_code, 302) 

    def test_password_reset(self):
        response = self.client.get(reverse('core:password_reset'))
        self.assertEqual(response.status_code, 200)
