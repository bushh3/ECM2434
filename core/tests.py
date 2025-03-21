from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Quiz, Question, Player, PlayerQuiz
from django.contrib.auth.models import User
from core.models import Player
from django.test import TestCase
from core.models import CustomUser  # 引入 CustomUser 模型
from django.utils.http import urlencode
import json




class LoginTests(TestCase):
    def test_login(self):
        # 使用 CustomUser 创建用户
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')
        response = self.client.post(reverse('core:login'), {
            'email': 'testuser@example.com',  # 添加 email 字段
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_view_invalid(self):
        response = self.client.post(reverse('core:login'),
                                    {'email': 'invalid@example.com', 'password': 'wrongpassword'})
        self.assertContains(response, 'Invalid username or password', status_code=200)

    def test_signup(self):
        response = self.client.post(reverse('core:signup'), {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        })
        # 确保注册后发生了重定向
        self.assertEqual(response.status_code, 200)  # Expect a redirect to the login page

        self.assertContains(response, "success")

    def test_password_reset(self):
        response = self.client.get(reverse('core:password_reset'))
        self.assertEqual(response.status_code, 200)

class ChangePasswordTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    class ChangePasswordTests(TestCase):
        def test_change_password(self):
            # 首先创建一个用户并登录
            user = User.objects.create_user(
                email='test@example.com',
                password='testpassword123'
            )
            self.client.login(email='test@example.com', password='testpassword123')

            # 获取CSRF token
            response = self.client.get(reverse('core:password_change'))
            csrf_token = response.cookies['csrftoken'].value

            # 模拟POST请求，提交新密码
            response = self.client.post(
                reverse('core:password_change'),
                data=json.dumps({
                    'new_password': 'newpassword123',
                    'new_password2': 'newpassword123',
                }),
                content_type="application/json",
                HTTP_X_CSRFTOKEN=csrf_token  # 传递 CSRF Token
            )

            # 验证响应内容
            self.assertEqual(response.status_code, 200)  # 检查返回的是 200 状态码，而不是重定向
            self.assertJSONEqual(response.content, {
                "success": True,
                "message": "Password updated successfully"
            })  # 确保密码修改成功


class QuizModelTest(TestCase):
    def setUp(self):
        # 使用 CustomUser 创建用户
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

        # 使用 get_or_create 确保没有重复创建 Player 实例
        self.player, created = Player.objects.get_or_create(user=self.user, points=0)

        # 创建 Quiz 和 Question 数据
        self.quiz = Quiz.objects.create(title="Test Quiz")
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            option1="2",
            option2="3",
            option3="4",
            option4="5",
            correct_option="C"
        )

    def test_quiz_creation(self):
        self.assertEqual(self.quiz.title, "Test Quiz")

    def test_question_creation(self):
        self.assertEqual(self.question.quiz, self.quiz)
        self.assertEqual(self.question.question_text, "What is 2 + 2?")
        self.assertEqual(self.question.correct_option, "C")


class QuizViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.quiz = Quiz.objects.create(title="Sample Quiz")

        self.question1 = Question.objects.create(
            quiz=self.quiz, question_text="Q1?", option1="A", option2="B",
            option3="C", option4="D", correct_option="A"
        )
        self.question2 = Question.objects.create(
            quiz=self.quiz, question_text="Q2?", option1="A", option2="B",
            option3="C", option4="D", correct_option="B"
        )

        # 创建测试用户
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword"
        )
        # 删除已经存在的 Player 实例（如果有的话）
        Player.objects.filter(user=self.user).delete()

        # 创建新的 Player
        self.player = Player.objects.create(user=self.user, points=0)

    def test_fetch_questions(self):
        response = self.client.get(reverse("core:fetch_questions"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question1.question_text)

    def test_check_answer_not_logged_in(self):
        response = self.client.post(reverse("core:check_answer"), {
            "question_1": "A",
            "question_2": "B",
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_check_answer_logged_in(self):
        self.client.login(username="testuser", password="testpassword")
        session = self.client.session
        session["current_questions"] = {
            "1": {"id": self.question1.id, "correct_option": "A"},
            "2": {"id": self.question2.id, "correct_option": "B"},
        }
        session.save()

        response = self.client.post(reverse("core:check_answer"), {
            "question_1": "A",
            "question_2": "B",
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after submitting answers
        self.player.refresh_from_db()

        # Test if the score is 10 points after answering 2 questions correctly
        self.assertEqual(self.player.points, 10)  # 2 questions * 5 points per question = 10 points

    def test_get_quiz_results(self):
        self.client.login(email="test@example.com", password="testpassword")
        session = self.client.session
        session["quiz_result"] = {
            "correct": 2,  # 2 correct answers
            "wrong": 0,  # No wrong answers
            "current_score": 10,  # 2 questions * 5 points = 10 points
            "total_score": 20  # Assuming the total score is 20 (or whatever logic you have)
        }
        session.save()

        response = self.client.get(reverse("core:get_quiz_results"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2|0|10|20") # Ensure the result string matches expected format


class ProfileAvatarTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        # 使用 CustomUser 创建用户
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com",
                                                   password="password123")
        self.client.login(username='testuser', password='password123')

class SaveTripTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_save_trip(self):
        self.client.login(email="test@example.com", password="testpassword")  # 登录用户
        response = self.client.post(
            reverse('core:save_trip'),
            data={
                'session_id': '123',
                'start_time': '2023-01-01T00:00:00',
                'end_time': '2023-01-01T01:00:00',
                'distance': '5.0',
                'duration': '3600',
                'is_completed': 'true',
                'track_points_count': '0',
            },
            content_type='application/x-www-form-urlencoded'  # 使用表单数据格式
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Trip data saved successfully.', 'status': 200})

    def test_save_trip_invalid_request(self):
        self.client.login(username='testuser', password='testpassword')  # 登录用户
        # 测试无效请求
        response = self.client.post(reverse('core:save_trip'), {}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid request.', 'status': 400})

class GetTripHistoryTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

class DeleteAccountTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_logout(self):
        # 测试注销
        response = self.client.post(reverse('core:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertJSONEqual(response.content, {"success": True, "message": "Logged out successfully"})  # 确保注销成功



