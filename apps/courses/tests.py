"""
课程资料管理 - 测试
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Course, CourseMaterial, Category

User = get_user_model()


class CourseModelTest(TestCase):
    """课程模型测试"""

    def setUp(self):
        self.category = Category.objects.create(name='技术培训', code='tech_training')
        self.instructor = User.objects.create_user(username='teacher', password='pass123')
        self.course = Course.objects.create(
            title='Python基础培训',
            description='Python编程基础课程',
            category=self.category,
            creator=self.instructor,
            status='published',
        )

    def test_course_creation(self):
        self.assertEqual(self.course.title, 'Python基础培训')
        self.assertTrue(self.course.status == 'published')

    def test_course_str(self):
        self.assertEqual(str(self.course), 'Python基础培训')

    def test_category_str(self):
        self.assertEqual(str(self.category), '技术培训')


class CourseViewTest(TestCase):
    """课程视图测试"""

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')
        self.course = Course.objects.create(
            title='测试课程', status='published'
        )

    def test_course_list_requires_login(self):
        response = self.client.get(reverse('courses:list'))
        self.assertEqual(response.status_code, 302)

    def test_course_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('courses:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_list.html')

    def test_course_detail(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('courses:detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_detail.html')
