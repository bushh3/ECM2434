from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class LoginViewTests(TestCase):
    def setUp(self):
       #create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_login_view_status_code(self):
       #Test that the login page renders correctly
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_valid_data(self):
        data = {
            'username': 'testuser',
            'password': 'password123',
        }
        response = self.client.post(reverse('core:login'), data)
        
        self.assertRedirects(response, '/')
    
    def test_login_invalid_data(self):
        #Error message when testing incorrect username or password
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('core:login'), data)

        # Bad password should return an error message
        self.assertFormError(response, 'form', None, 'Invalid details: please try again')
    
    def test_login_csrf_token(self):
        data = {
            'username': 'testuser',
            'password': 'password123',
        }
        response = self.client.post(reverse('core:login'), data, HTTP_X_CSRFTOKEN='invalid_csrf_token')
        
        # CSRF validation fails should return to 403
        self.assertEqual(response.status_code, 403)
    
    def test_login_redirect_to_signup(self):
        #Test login page redirects to registration page
        response = self.client.get(reverse('core:signup'))
        
        # Register if the page is rendered correctly
        self.assertEqual(response.status_code, 200)
    
    def test_login_ajax_loading_state(self):
        #Simulate front-end JavaScript requests, test load status display
        data = {
            'username': 'testuser',
            'password': 'password123',
        }
        # Simulated AJAX request
        response = self.client.post(reverse('core:login'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Simulate returning a JSON response to indicate that the request was successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content), {'status': 'success'})

