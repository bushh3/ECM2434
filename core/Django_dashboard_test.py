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
        # 创建一个测试用户
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_login_redirect(self):
        # 未登录用户访问主页应该被重定向到登录页面
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('core:login'))

    def test_login_valid_user(self):
        # 使用测试用户登录
        self.client.login(username='testuser', password='testpassword')
        
        # 已登录用户应能访问主页
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
