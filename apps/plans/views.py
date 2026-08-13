"""
培训计划与任务分配 - 视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.urls import reverse_lazy

from .models import TrainingPlan, PlanTask, TaskAssignment, MandatoryTrainee
from apps.users.models import User


def _is_admin_or_manager(user):
    """检查用户是否为管理员或培训管理员"""
    if not user.is_authenticated:
        return False
    return user.is_superuser or (user.role and user.role.code in ('admin', 'training_manager'))


@method_decorator(login_required, name='dispatch')
class PlanListView(ListView):
    """培训计划列表"""
    model = TrainingPlan
    template_name = 'plans/plan_list.html'
    context_object_name = 'plans'
    paginate_by = 10

    def get_queryset(self):
        queryset = TrainingPlan.objects.all()
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = TrainingPlan.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        return context


@method_decorator(login_required, name='dispatch')
class PlanDetailView(DetailView):
    """计划详情，显示任务列表和各用户完成情况"""
    model = TrainingPlan
    template_name = 'plans/plan_detail.html'
    context_object_name = 'plan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all().select_related('course', 'exam')

        # 获取当前用户的任务分配状态
        if self.request.user.is_authenticated:
            context['user_assignments'] = TaskAssignment.objects.filter(
                task__plan=self.object,
                user=self.request.user
            ).select_related('task')

        # 获取每个任务的所有分配情况（用于展示各用户完成情况）
        task_assignments = {}
        for task in context['tasks']:
            assignments = TaskAssignment.objects.filter(
                task=task
            ).select_related('user').order_by('user__username')
            task_assignments[task.id] = assignments
        context['task_assignments'] = task_assignments

        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(_is_admin_or_manager), name='dispatch')
class PlanCreateView(CreateView):
    """创建培训计划（选择课程、考试、设置时间）"""
    model = TrainingPlan
    template_name = 'plans/plan_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'deadline', 'status',
              'is_mandatory', 'require_exam_pass', 'allow_retake', 'max_attempts',
              'courses', 'exams']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, '培训计划创建成功！')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('plans:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '创建培训计划'
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(_is_admin_or_manager), name='dispatch')
class PlanEditView(UpdateView):
    """编辑培训计划"""
    model = TrainingPlan
    template_name = 'plans/plan_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'deadline', 'status',
              'is_mandatory', 'require_exam_pass', 'allow_retake', 'max_attempts',
              'courses', 'exams']

    def form_valid(self, form):
        messages.success(self.request, '培训计划更新成功！')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('plans:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '编辑培训计划'
        return context


@login_required
@user_passes_test(_is_admin_or_manager)
def assign_task_view(request, pk):
    """分配任务给用户（支持批量选择用户）"""
    plan = get_object_or_404(TrainingPlan, pk=pk)

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        if not task_id:
            messages.error(request, '请选择要分配的任务。')
            return redirect('plans:assign', pk=pk)

        task = get_object_or_404(PlanTask, pk=task_id, plan=plan)
        user_ids = request.POST.getlist('users')

        if not user_ids:
            messages.warning(request, '请至少选择一个用户。')
        else:
            created_count = 0
            skipped_count = 0
            for user_id in user_ids:
                _, created = TaskAssignment.objects.get_or_create(
                    task=task,
                    user_id=user_id,
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

            msg = f'已成功分配任务给 {created_count} 位用户。'
            if skipped_count > 0:
                msg += f'（{skipped_count} 位用户已有该任务，已跳过）'
            messages.success(request, msg)

        return redirect('plans:detail', pk=pk)

    # GET: 显示任务分配页面
    tasks = plan.tasks.all().select_related('course', 'exam')
    users = User.objects.all().order_by('username')

    return render(request, 'plans/assign_task.html', {
        'plan': plan,
        'tasks': tasks,
        'users': users,
    })


@login_required
def my_tasks_view(request):
    """当前用户的任务列表（学员端）"""
    assignments = TaskAssignment.objects.filter(
        user=request.user
    ).select_related('task', 'task__plan', 'task__course', 'task__exam').order_by(
        'task__plan__end_date', 'task__deadline', 'task__order'
    )

    status_filter = request.GET.get('status')
    if status_filter:
        assignments = assignments.filter(status=status_filter)

    return render(request, 'plans/my_tasks.html', {
        'assignments': assignments,
        'status_choices': TaskAssignment.STATUS_CHOICES,
        'current_status': request.GET.get('status', ''),
    })


@login_required
def complete_task_view(request, pk):
    """标记任务完成（学员端）"""
    assignment = get_object_or_404(
        TaskAssignment,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':
        if assignment.status == 'completed':
            messages.warning(request, '该任务已经完成了。')
        else:
            assignment.status = 'completed'
            assignment.save()
            messages.success(request, f'任务 "{assignment.task.title}" 已标记为完成！')

    return redirect('plans:my_tasks')


# ============ 管理员：强制培训管理 ============

@login_required
@user_passes_test(_is_admin_or_manager)
def mandatory_trainee_manage(request, pk):
    """管理强制培训人员名单"""
    plan = get_object_or_404(TrainingPlan, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            user_ids = request.POST.getlist('users')
            added = 0
            for uid in user_ids:
                _, created = MandatoryTrainee.objects.get_or_create(plan=plan, user_id=uid)
                if created:
                    added += 1
            messages.success(request, f'已添加 {added} 名强制培训人员')
        elif action == 'remove':
            trainee_id = request.POST.get('trainee_id')
            MandatoryTrainee.objects.filter(pk=trainee_id, plan=plan).delete()
            messages.success(request, '已移除')
        elif action == 'add_department':
            dept_id = request.POST.get('department')
            from apps.users.models import User
            users = User.objects.filter(department_id=dept_id, is_active=True)
            added = 0
            for u in users:
                _, created = MandatoryTrainee.objects.get_or_create(plan=plan, user=u)
                if created:
                    added += 1
            messages.success(request, f'已添加部门下 {added} 名人员')
        return redirect('plans:mandatory_trainee', pk=pk)

    trainees = plan.get_mandatory_trainees()
    from apps.users.models import User, Department
    users = User.objects.filter(is_active=True).exclude(
        id__in=trainees.values_list('user_id', flat=True)
    ).order_by('username')
    departments = Department.objects.all()

    return render(request, 'plans/mandatory_trainee.html', {
        'plan': plan,
        'trainees': trainees,
        'users': users,
        'departments': departments,
    })


@login_required
@user_passes_test(_is_admin_or_manager)
def mandatory_training_overview(request):
    """强制培训总览 - 管理员查看所有强制培训"""
    plans = TrainingPlan.objects.filter(is_mandatory=True).order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        plans = plans.filter(status=status_filter)

    # 统计每个计划的完成情况
    plan_stats = []
    for plan in plans:
        trainees = plan.get_mandatory_trainees()
        total = trainees.count()
        passed = trainees.filter(status='passed').count()
        pending = trainees.filter(status='pending').count()
        failed = trainees.filter(status='failed').count()
        overdue = trainees.filter(status='overdue').count()
        plan_stats.append({
            'plan': plan,
            'total': total,
            'passed': passed,
            'pending': pending,
            'failed': failed,
            'overdue': overdue,
            'pass_rate': f'{passed}/{total}' if total > 0 else '0/0',
        })

    return render(request, 'plans/mandatory_overview.html', {
        'plan_stats': plan_stats,
        'status_choices': TrainingPlan.STATUS_CHOICES,
        'current_status': status_filter or '',
    })
