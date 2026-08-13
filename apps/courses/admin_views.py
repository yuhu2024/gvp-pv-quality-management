"""
管理员视图 - 课程分类管理
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from .models import Category


def is_admin(user):
    """检查是否为管理员"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class CategoryListView(ListView):
    """课程分类列表"""
    model = Category
    template_name = 'courses/admin/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.all().order_by('order', 'name')


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class CategoryCreateView(CreateView):
    """创建课程分类"""
    model = Category
    template_name = 'courses/admin/category_form.html'
    fields = ['parent', 'name', 'code', 'description', 'order', 'is_active']
    success_url = reverse_lazy('courses:admin_category_list')

    def form_valid(self, form):
        messages.success(self.request, f'分类「{form.instance.name}」创建成功！')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '创建课程分类'
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class CategoryEditView(UpdateView):
    """编辑课程分类"""
    model = Category
    template_name = 'courses/admin/category_form.html'
    fields = ['parent', 'name', 'code', 'description', 'order', 'is_active']
    success_url = reverse_lazy('courses:admin_category_list')

    def form_valid(self, form):
        messages.success(self.request, f'分类「{form.instance.name}」更新成功！')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '编辑课程分类'
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class CategoryDeleteView(DeleteView):
    """删除课程分类"""
    model = Category
    template_name = 'courses/admin/category_confirm_delete.html'
    success_url = reverse_lazy('courses:admin_category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '分类已删除！')
        return super().delete(request, *args, **kwargs)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """管理员首页 - 基础配置入口"""
    from apps.courses.models import Category, Course
    from apps.plans.models import TrainingPlan, MandatoryTrainee
    from apps.exams.models import Exam
    from apps.users.models import User

    context = {
        'category_count': Category.objects.count(),
        'course_count': Course.objects.count(),
        'exam_count': Exam.objects.count(),
        'plan_count': TrainingPlan.objects.count(),
        'mandatory_plan_count': TrainingPlan.objects.filter(is_mandatory=True).count(),
        'mandatory_trainee_count': MandatoryTrainee.objects.count(),
        'user_count': User.objects.filter(is_active=True).count(),
    }
    return render(request, 'admin_dashboard.html', context)
