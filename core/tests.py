from django.test import TestCase
from django.urls import reverse

class LoginTests(TestCase):
    def test_login(self):
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        response = self.client.post(reverse('core:signup'), {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)

    def test_password_reset(self):
        response = self.client.get(reverse('core:password_reset'))
        self.assertEqual(response.status_code, 200)


# Create your tests here.
