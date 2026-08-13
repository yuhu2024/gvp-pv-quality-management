"""
培训计划与任务分配 - 测试
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from .models import TrainingPlan, PlanTask, TaskAssignment

User = get_user_model()


class PlanModelTest(TestCase):
    """培训计划模型测试"""

    def setUp(self):
        self.creator = User.objects.create_user(username='admin', password='pass123')
        self.plan = TrainingPlan.objects.create(
            title='2024年度新员工培训计划',
            description='针对新入职员工的综合培训',
            status='published',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            creator=self.creator,
        )
        self.task = PlanTask.objects.create(
            plan=self.plan,
            title='学习公司规章制度',
            task_type='course',
            deadline=date.today() + timedelta(days=7),
        )

    def test_plan_creation(self):
        self.assertEqual(self.plan.title, '2024年度新员工培训计划')
        self.assertEqual(self.plan.status, 'published')

    def test_task_creation(self):
        self.assertEqual(self.task.plan, self.plan)
        self.assertEqual(self.task.task_type, 'course')

    def test_task_assignment(self):
        user = User.objects.create_user(username='student1', password='pass123')
        assignment = TaskAssignment.objects.create(
            task=self.task,
            user=user,
        )
        self.assertEqual(assignment.status, 'pending')
        self.assertEqual(str(assignment), f'{user} - {self.task.title} (待开始)')


class PlanViewTest(TestCase):
    """培训计划视图测试"""

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')
        self.plan = TrainingPlan.objects.create(
            title='测试计划', status='published',
            start_date=date.today(), end_date=date.today() + timedelta(days=30),
        )

    def test_plan_list_requires_login(self):
        response = self.client.get(reverse('plans:list'))
        self.assertEqual(response.status_code, 302)

    def test_plan_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('plans:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plans/plan_list.html')
