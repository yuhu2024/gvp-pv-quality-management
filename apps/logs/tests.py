"""
学习痕迹记录 - 测试
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import LearningLog, OperationLog

User = get_user_model()


class LearningLogModelTest(TestCase):
    """学习记录模型测试"""

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')
        self.log = LearningLog.objects.create(
            user=self.user,
            action='view_course',
            detail='浏览了Python基础培训课程',
            ip_address='127.0.0.1',
        )

    def test_log_creation(self):
        self.assertEqual(self.log.user, self.user)
        self.assertEqual(self.log.action, 'view_course')

    def test_log_str(self):
        self.assertIn('浏览课程', str(self.log))


class OperationLogModelTest(TestCase):
    """操作日志模型测试"""

    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass123')
        self.log = OperationLog.objects.create(
            user=self.user,
            action='login',
            ip_address='127.0.0.1',
            detail='用户登录系统',
        )

    def test_log_creation(self):
        self.assertEqual(self.log.user, self.user)
        self.assertEqual(self.log.action, 'login')

    def test_log_str(self):
        self.assertIn('登录', str(self.log))


class LogViewTest(TestCase):
    """日志视图测试"""

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')

    def test_learning_log_requires_login(self):
        response = self.client.get(reverse('logs:learning_log'))
        self.assertEqual(response.status_code, 302)

    def test_learning_log_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logs:learning_log'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logs/learning_log.html')
