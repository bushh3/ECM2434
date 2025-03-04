from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Quiz, Question, Player, PlayerQuiz

class LoginTests(TestCase):
    def test_login(self):
        # Use the appropriate user name and password in the test
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            "email": "test@example.com",
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


class QuizModelTest(TestCase):
    def setUp(self):
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
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword"
        )
        self.player = Player.objects.create(user=self.user, points=0)

    def test_fetch_questions(self):
        """Test the interface that gets the problem"""
        response = self.client.get(reverse("core:fetch_questions"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question1.question_text)

    def test_check_answer_not_logged_in(self):
        """Users who are not logged in cannot submit answers"""
        response = self.client.post(reverse("core:check_answer"), {
            "question_1": "A",
            "question_2": "B",
        })
        self.assertEqual(response.status_code, 302)  # 302 = Redirect to login

    def test_check_answer_logged_in(self):
        """Test submission answer"""
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
        self.assertEqual(response.status_code, 302)
        self.player.refresh_from_db()
        self.assertEqual(self.player.points, 10)

    def test_get_quiz_results(self):
        """Test Get test results"""
        self.client.login(email="test@example.com", password="testpassword")
        session = self.client.session
        session["quiz_result"] = {
            "correct": 2,
            "wrong": 0,
            "current_score": 10,
            "total_score": 20
        }
        session.save()

        response = self.client.get(reverse("core:get_quiz_results"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2|0|10|20")

