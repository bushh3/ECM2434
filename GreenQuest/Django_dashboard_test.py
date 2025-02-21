# core/views.py
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to GreenQuest!")

# core/tests.py
from django.test import TestCase
from django.urls import reverse

class HomePageTest(TestCase):
    def test_homepage_status_code(self):
        # Generate the URL for the home page
        url = reverse('home')
        response = self.client.get(url)
        
        #200 indicating that the page successfully loaded
        self.assertEqual(response.status_code, 200)

    def test_homepage_content(self):
        url = reverse('home')
        response = self.client.get(url)
        #indicate message successfully
        self.assertContains(response, "Welcome to GreenQuest!")

# core/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

class LoginTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_login_redirect(self):
        # Non-logged in users accessing the home page should be redirected to the login page
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('core:login'))

    def test_login_valid_user(self):
        # Test User log in
        self.client.login(username='testuser', password='testpassword')
        
        # Logged in users should be able to access the home page
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


# core/models.py
from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# core/tests.py
from django.test import TestCase
from .models import Task

class TaskModelTest(TestCase):

    def test_create_task(self):
        # Create a new task
        task = Task.objects.create(title="Test Task", description="This is a test task.")
        
        # Check whether the task has been saved successfully
        self.assertEqual(Task.objects.count(), 1)
        
        # Verify the contents of the task field
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "This is a test task.")
        self.assertFalse(task.completed)

    def test_task_str(self):
        task = Task.objects.create(title="Test Task", description="Task description")
        
        # verifies the return value of the __str__ method
        self.assertEqual(str(task), "Test Task")


# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 主页视图的路由
    path('login/', views.login_view, name='login'),  # 登录页面的路由
]

# core/tests.py
from django.test import TestCase
from django.urls import reverse

class URLTest(TestCase):

    def test_home_url(self):
        # Check that the home page URL points to the correct view
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        # Check that the login page URL is correct
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

