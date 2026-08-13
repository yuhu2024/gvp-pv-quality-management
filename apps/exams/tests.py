"""
在线考试 - 测试
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Exam, Question, ExamAttempt
from apps.courses.models import Course

User = get_user_model()


class ExamModelTest(TestCase):
    """考试模型测试"""

    def setUp(self):
        self.course = Course.objects.create(title='测试课程', status='published')
        self.exam = Exam.objects.create(
            title='Python基础考试',
            exam_type='post_test',
            course=self.course,
            duration=60,
            total_score=100,
            pass_score=60,
            is_published=True,
        )
        self.question = Question.objects.create(
            exam=self.exam,
            content='Python的Web框架是？',
            question_type='single_choice',
            score=10,
            options='{"A": "Flask", "B": "Django", "C": "FastAPI", "D": "Tornado"}',
            answer='B',
            explanation='Django是Python最流行的Web框架之一。',
            order=1,
        )

    def test_exam_creation(self):
        self.assertEqual(self.exam.title, 'Python基础考试')
        self.assertEqual(self.exam.total_score, 100)

    def test_question_creation(self):
        self.assertEqual(self.question.exam, self.exam)
        self.assertEqual(self.question.score, 10)


class ExamViewTest(TestCase):
    """考试视图测试"""

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')
        self.exam = Exam.objects.create(
            title='测试考试', is_published=True, duration=30
        )

    def test_exam_list_requires_login(self):
        response = self.client.get(reverse('exams:list'))
        self.assertEqual(response.status_code, 302)

    def test_exam_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('exams:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exams/exam_list.html')
