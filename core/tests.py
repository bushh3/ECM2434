from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Quiz, Question
from django.contrib.auth.models import User
from core.models import Player
from django.test import TestCase
from core.models import CustomUser  # 引入 CustomUser 模型
from django.utils.http import urlencode
import json
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Profile, WalkingChallenge
from core.models import RecyclingBin, Player, ScanRecord
from datetime import date

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

        def test_change_password_validation_error(self):
            # 发送 POST 请求更改密码，使用无效的密码
            data = {'new_password': 'short'}
            response = self.client.post(reverse('core:change_password'), data=json.dumps(data),
                                        content_type='application/json')

            # 检查响应状态码和内容
            self.assertEqual(response.status_code, 400)
            self.assertFalse(response.json()['success'])
            self.assertIn('error', response.json())





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
        self.client.login(email="test@example.com", password="testpassword")
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
        import time
        time.sleep(1)

        self.player = Player.objects.get(user=self.user)

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
        self.assertContains(response, "2|0|10|20")  # Ensure the result string matches expected format


@override_settings(CSRF_COOKIE_SECURE=False, CSRF_COOKIE_HTTPONLY=False)
class ProfileAvatarTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        # 确保 Profile 对象已创建
        self.profile, created = Profile.objects.get_or_create(user=self.user)
        self.client.login(email="test@example.com", password="testpassword")

    def test_upload_avatar(self):
        # 创建模拟文件
        avatar_file = SimpleUploadedFile("test_avatar.jpg", b"file_content", content_type="image/jpeg")

        # 发送 POST 请求，跟随重定向
        response = self.client.post(
            reverse('core:upload_avatar'),
            {'avatar': avatar_file},
            follow=True  # 跟随重定向
        )

        # 检查响应状态码和内容
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('avatarUrl', response.json())

        # 检查头像是否保存到数据库
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.avatar_url)

        # 清理上传的文件
        if self.user.profile.avatar_url:
            avatar_path = os.path.join(settings.MEDIA_ROOT, self.user.profile.avatar_url)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

    def test_get_user_profile(self):
        # 发送 GET 请求获取用户信息
        response = self.client.get(reverse('core:get_user_profile'))

        # 检查响应状态码和内容
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['username'], self.user.username)
        self.assertEqual(response.json()['email'], self.user.email)
        self.assertEqual(response.json()['avatar_url'], f"{settings.MEDIA_URL}avatars/fox.jpg")

    def test_get_avatar(self):
        # 发送 GET 请求获取用户头像
        response = self.client.get(reverse('core:get_avatar'))

        # 检查响应状态码和内容
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['avatar_url'], f"{settings.MEDIA_URL}avatars/fox.jpg")

    def test_update_user_profile(self):
        # 发送 PUT 请求更新用户信息
        data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.put(reverse('core:update_user_profile'), data=json.dumps(data),
                                   content_type='application/json')

        # 检查响应状态码和内容
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Profile updated successfully')
        # 检查用户信息是否更新
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.last_name, 'User')



    



class SaveTripTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(email="test@example.com", password="testpassword")

    def test_save_trip(self):
        self.client.login(email="test@example.com", password="testpassword")  # 登录用户
        data={
                'session_id': '123',
                'start_time': '2023-01-01T00:00:00',
                'end_time': '2023-01-01T01:00:00',
                'distance': '5.0',
                'duration': '3600',
                'is_completed': 'true',
                'track_points_count': '0',
        }

        response = self.client.post(
            reverse('core:save_trip'),
            data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Trip data saved successfully.', 'status': 200})

    def test_save_trip_invalid_request(self):
        self.client.login(email="test@example.com", password="testpassword")
        # 测试没有提供必需字段时的请求
        response = self.client.post(reverse('core:save_trip'), {
            'session_id': '',
            'start_time': '',
            'end_time': '',
            'distance': '',
            'duration': '',
            'is_completed': '',
            'track_points_count': '',
        }, 
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'session_id cannot be empty'})


CustomUser = get_user_model()

class GetTripHistoryTests(TestCase):

    def setUp(self):
        # 创建用户并登录
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client = Client()
        self.client.login(email="test@example.com", password="testpassword")  # 使用 email 登录

    def test_get_trip_history_unauthenticated(self):
        # 未登录用户访问
        self.client.logout()  # 登出用户
        response = self.client.get(reverse('core:get_trip_history'))
        # 检查是否重定向到登录页面
        self.assertEqual(response.status_code, 302)  # 302 是重定向状态码
        self.assertIn('/login/', response.url)  # 检查是否重定向到登录页面

    def test_get_trip_history_no_trips(self):
        # 用户没有行程记录
        response = self.client.get(reverse('core:get_trip_history'))
        # 检查响应状态码和内容
        self.assertEqual(response.status_code, 200)
        self.assertIn('No travel records yet', response.content.decode())  # 检查是否返回无记录提示

    def test_get_trip_history_with_trips(self):
        # 创建 Player 对象（如果不存在）
        if not hasattr(self.user, 'player'):
            Player.objects.create(user=self.user, points=0)

        # 创建行程记录
        WalkingChallenge.objects.create(
            player=self.user.player,
            start_time='2023-01-01T00:00:00',
            end_time='2023-01-01T01:00:00',
            distance=5.0,
            duration=3600,  # 3600 秒 = 60 分钟
            is_completed=True,
            points_earned=10
        )

        # 发送 GET 请求
        response = self.client.get(reverse('core:get_trip_history'))
        # 检查响应状态码和内容
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # 检查返回的 HTML 是否正确
        self.assertIn('Activity History', content)  # 检查标题
        self.assertIn('5.0 km', content)  # 检查距离
        self.assertIn('60 min 0 sec', content)  # 检查时长
        self.assertIn('10 Points', content)  # 检查积分
        self.assertIn('Completed', content)  # 检查状态

CustomUser = get_user_model()


class DeleteAccountTests(TestCase):
    def setUp(self):
        # 创建用户并登录
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client = Client()
        self.client.login(email="test@example.com", password="testpassword")  # 使用 email 登录

    def test_delete_account_unauthenticated(self):
        # 未登录用户访问
        self.client.logout()  # 登出用户
        response = self.client.delete(reverse('core:delete_account'))

        # 检查是否重定向到登录页面
        self.assertEqual(response.status_code, 302)  # 302 是重定向状态码
        self.assertIn('/login/', response.url)  # 检查是否重定向到登录页面

    def test_delete_account_authenticated(self):
        # 登录用户发送 DELETE 请求
        response = self.client.delete(reverse('core:delete_account'))
        # 检查响应状态码和内容
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Account deleted successfully')

        # 检查用户是否被删除
        self.assertFalse(CustomUser.objects.filter(email='test@example.com').exists())

    def test_delete_account_invalid_method(self):
        # 发送非 DELETE 请求（例如 GET）
        response = self.client.get(reverse('core:delete_account'))
        # 检查是否返回 405 错误
        self.assertEqual(response.status_code, 405)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], 'Invalid request method')
        

class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(email="test@example.com", password="testpassword")

    def test_logout(self):
        # 登录用户
        self.client.login(email="test@example.com", password="testpassword")

        # 发送 POST 请求到登出视图
        response = self.client.post(reverse('core:logout'))  # 确保是 POST 请求

        # 确保状态码是 200（不会重定向）
        self.assertEqual(response.status_code, 200)

        # 确保返回的 JSON 响应是成功的
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             '{"success": true, "message": "Logged out successfully"}')



class RecyclingBinTestCase(TestCase):
    def setUp(self):
        # 创建一些回收点对象，确保它们在测试时存在
        RecyclingBin.objects.create(location_name="Amory Building", qr_code="RECYCLE-001")
        RecyclingBin.objects.create(location_name="Forum", qr_code="RECYCLE-002")
        RecyclingBin.objects.create(location_name="Harrison", qr_code="RECYCLE-003")
        RecyclingBin.objects.create(location_name="Sports Park", qr_code="RECYCLE-004")

    def test_recycling_bin_view(self):
        # 发送GET请求到回收页面
        response = self.client.get(reverse('core:recycling'))  # 确保在urls.py中定义了这个url

        # 确保返回的响应内容包含回收点名称
        self.assertContains(response, 'Amory Building')  # 确保 Amory Building 出现在页面
        self.assertContains(response, 'Forum')  # 确保 Forum 出现在页面
        self.assertContains(response, 'Harrison')  # 确保 Harrison 出现在页面
        self.assertContains(response, 'Sports Park')  # 确保 Sports Park 出现在页面

class ScanQRCodeViewTests(TestCase):
    def setUp(self):
        # 创建测试用户并登录
        self.user = get_user_model().objects.create_user(
            username='testuser', email='test@example.com', password='testpassword'
        )
        self.client.login(email="test@example.com", password="testpassword")

        # 创建测试的回收点
        RecyclingBin.objects.create(qr_code="QR123", location_name="Bin 1")

    def test_scan_qr_code_success(self):
        # 模拟扫描二维码，发送POST请求
        response = self.client.post(reverse('core:scan_qr_code'), {'qrCode': 'QR123'})

        # 检查返回的状态码和响应内容
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "status=success")

    def test_scan_qr_code_invalid_qr(self):
        response = self.client.post(reverse('core:scan_qr_code'), {'qrCode': 'InvalidQR'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "status=invalid&message=Invalid QR code. Please try again.")

    def test_scan_qr_code_already_scanned(self):
        ScanRecord.objects.create(user=self.user, scan_date=date.today(), qr_code="QR123")
        response = self.client.post(reverse('core:scan_qr_code'), {'qrCode': 'QR123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "status=already_scanned_today")

    def test_scan_qr_code_invalid_method(self):
        response = self.client.get(reverse('core:scan_qr_code'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "status=error&message=Invalid request method")

class GetUserInfoTests(TestCase):
    def setUp(self):
        # Create the test user if not already created
        self.user = get_user_model().objects.create_user(
            username='testuser', email='test@example.com', password='testpassword'
        )
        self.client.login(email="test@example.com", password="testpassword")

        # Ensure no Player already exists for the user
        Player.objects.filter(user=self.user).delete()

        # Create the Player object with points set to 100
        self.player = Player.objects.create(user=self.user, points=100)

    def test_get_user_info_success(self):
        # Send GET request to retrieve user info
        response = self.client.get(reverse('core:get_user_info'))

        # Print the response for debugging
        print(response.content)

        # Verify the response contains the expected points value
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "points=100")

    def test_get_user_info_user_not_found(self):
        self.client.logout()
        response = self.client.get(reverse('core:get_user_info'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:login') + '?next=' + reverse('core:get_user_info'))


