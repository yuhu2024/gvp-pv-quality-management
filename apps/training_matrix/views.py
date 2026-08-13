"""
培训矩阵 - 视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count, Prefetch

from .models import TrainingMatrix, TrainingMatrixItem, UserMatrixProgress
from apps.courses.models import Course, CourseProgress
from apps.users.models import Department


# ===================== 管理员视图 =====================

@login_required
def matrix_list_view(request):
    if not request.user.is_staff:
        messages.error(request, '权限不足')
        return redirect('users:dashboard')
    """培训矩阵列表"""
    matrices = TrainingMatrix.objects.select_related(
        'department'
    ).prefetch_related(
        'items'
    ).all().order_by('department__name', 'title')

    # 统计信息：每个矩阵的完成人数
    for m in matrices:
        m.completed_users = UserMatrixProgress.objects.filter(
            item__matrix=m, status='completed'
        ).values('user').distinct().count()
        m.total_users = UserMatrixProgress.objects.filter(
            item__matrix=m
        ).values('user').distinct().count()

    departments = Department.objects.all()

    return render(request, 'training_matrix/matrix_list.html', {
        'matrices': matrices,
        'departments': departments,
    })


@login_required
def matrix_create_view(request):
    if not request.user.is_staff:
        messages.error(request, '权限不足')
        return redirect('users:dashboard')
    """创建培训矩阵"""
    departments = Department.objects.all()
    courses = Course.objects.filter(status='published')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        department_id = request.POST.get('department')
        description = request.POST.get('description', '').strip()

        if not title or not department_id:
            messages.error(request, '请填写矩阵名称并选择部门')
            return render(request, 'training_matrix/matrix_form.html', {
                'departments': departments, 'courses': courses, 'is_create': True
            })

        matrix = TrainingMatrix.objects.create(
            title=title,
            department_id=department_id,
            description=description,
        )

        # 处理条目
        course_ids = request.POST.getlist('course_ids[]')
        positions = request.POST.getlist('positions[]')
        required_months = request.POST.getlist('required_months[]')
        priorities = request.POST.getlist('priorities[]')
        is_required_list = request.POST.getlist('is_required[]')

        for i, course_id in enumerate(course_ids):
            if not course_id:
                continue
            pos = positions[i] if i < len(positions) else ''
            months = int(required_months[i]) if i < len(required_months) else 3
            pri = int(priorities[i]) if i < len(priorities) else 2
            is_req = (str(i) in is_required_list) if is_required_list else True

            TrainingMatrixItem.objects.create(
                matrix=matrix,
                course_id=course_id,
                position=pos,
                required_months=months,
                priority=pri,
                is_required=is_req,
                order=i,
            )

        messages.success(request, f'培训矩阵「{matrix.title}」创建成功！')
        return redirect('training_matrix:detail', pk=matrix.pk)

    return render(request, 'training_matrix/matrix_form.html', {
        'departments': departments, 'courses': courses, 'is_create': True,
    })


@login_required
def matrix_detail_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, '权限不足')
        return redirect('users:dashboard')
    """培训矩阵详情"""
    matrix = get_object_or_404(
        TrainingMatrix.objects.select_related('department').prefetch_related(
            Prefetch('items', queryset=TrainingMatrixItem.objects.select_related('course'))
        ),
        pk=pk
    )

    # 获取所有岗位列表
    positions = matrix.items.values_list('position', flat=True).distinct()

    # 获取各部门用户及完成统计
    users = matrix.department.user_set.filter(is_active=True).select_related('role')

    # 构建用户进度数据
    user_progress_list = []
    all_progress = UserMatrixProgress.objects.filter(
        item__matrix=matrix
    ).select_related('item__course')

    progress_map = {}
    for p in all_progress:
        key = (p.user_id, p.item_id)
        progress_map[key] = p

    for user in users:
        completed = 0
        total = matrix.items.count()
        overdue = 0
        for item in matrix.items.all():
            prog = progress_map.get((user.id, item.id))
            if prog:
                if prog.status == 'completed':
                    completed += 1
                elif prog.status == 'overdue':
                    overdue += 1

        user_progress_list.append({
            'user': user,
            'completed': completed,
            'total': total,
            'overdue': overdue,
            'progress_pct': int(completed / total * 100) if total > 0 else 0,
        })

    return render(request, 'training_matrix/matrix_detail.html', {
        'matrix': matrix,
        'positions': positions,
        'user_progress_list': user_progress_list,
    })


@login_required
def matrix_edit_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, '权限不足')
        return redirect('users:dashboard')
    """编辑培训矩阵"""
    matrix = get_object_or_404(
        TrainingMatrix.objects.select_related('department').prefetch_related('items__course'),
        pk=pk
    )
    departments = Department.objects.all()
    courses = Course.objects.filter(status='published')

    if request.method == 'POST':
        matrix.title = request.POST.get('title', '').strip()
        matrix.department_id = request.POST.get('department')
        matrix.description = request.POST.get('description', '').strip()
        matrix.save()

        # 删除旧条目，重新创建
        matrix.items.all().delete()

        course_ids = request.POST.getlist('course_ids[]')
        positions = request.POST.getlist('positions[]')
        required_months = request.POST.getlist('required_months[]')
        priorities = request.POST.getlist('priorities[]')

        for i, course_id in enumerate(course_ids):
            if not course_id:
                continue
            pos = positions[i] if i < len(positions) else ''
            months = int(required_months[i]) if i < len(required_months) else 3
            pri = int(priorities[i]) if i < len(priorities) else 2

            TrainingMatrixItem.objects.create(
                matrix=matrix,
                course_id=course_id,
                position=pos,
                required_months=months,
                priority=pri,
                is_required=True,
                order=i,
            )

        messages.success(request, f'培训矩阵「{matrix.title}」更新成功！')
        return redirect('training_matrix:detail', pk=matrix.pk)

    return render(request, 'training_matrix/matrix_form.html', {
        'matrix': matrix,
        'departments': departments,
        'courses': courses,
        'is_create': False,
    })


@login_required
def matrix_delete_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, '权限不足')
        return redirect('users:dashboard')
    """删除培训矩阵"""
    matrix = get_object_or_404(TrainingMatrix, pk=pk)
    if request.method == 'POST':
        matrix.delete()
        messages.success(request, '培训矩阵已删除')
        return redirect('training_matrix:list')
    return render(request, 'training_matrix/matrix_confirm_delete.html', {
        'matrix': matrix
    })


@login_required
def matrix_assign_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, '权限不足')
        return redirect('users:dashboard')
    """分配矩阵到用户 - 为部门下所有用户创建进度记录"""
    matrix = get_object_or_404(
        TrainingMatrix.objects.prefetch_related('items__course'),
        pk=pk
    )

    if request.method == 'POST':
        users = matrix.department.user_set.filter(is_active=True)
        created_count = 0
        skipped_count = 0

        with transaction.atomic():
            for user in users:
                for item in matrix.items.all():
                    _, created = UserMatrixProgress.objects.get_or_create(
                        user=user,
                        item=item,
                        defaults={
                            'matrix': matrix,
                            'status': 'pending',
                            'due_date': timezone.now().date() + timedelta(days=item.required_months * 30),
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        skipped_count += 1

        messages.success(
            request,
            f'分配完成！新增 {created_count} 条进度记录，跳过 {skipped_count} 条已有记录'
        )
        return redirect('training_matrix:detail', pk=matrix.pk)

    users = matrix.department.user_set.filter(is_active=True)
    return render(request, 'training_matrix/matrix_assign.html', {
        'matrix': matrix,
        'users': users,
    })


@login_required
def matrix_sync_progress_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, '权限不足')
        return redirect('users:dashboard')
    """同步矩阵进度 - 从 CourseProgress 更新用户矩阵进度"""
    matrix = get_object_or_404(TrainingMatrix, pk=pk)
    updated_count = 0

    with transaction.atomic():
        user_progress_list = UserMatrixProgress.objects.filter(
            item__matrix=matrix
        ).select_related('user', 'item')

        for up in user_progress_list:
            try:
                cp = CourseProgress.objects.get(
                    user=up.user,
                    course=up.item.course
                )
                up.course_progress = cp
                if cp.is_completed and up.status != 'completed':
                    up.status = 'completed'
                    up.completed_at = cp.completed_at or timezone.now()
                    up.save()
                    updated_count += 1
                elif not cp.is_completed and up.status == 'pending':
                    up.status = 'in_progress'
                    up.save()
                    updated_count += 1
                else:
                    up.save()
            except CourseProgress.DoesNotExist:
                pass

    messages.success(request, f'同步完成！更新了 {updated_count} 条记录')
    return redirect('training_matrix:detail', pk=matrix.pk)


# ===================== 用户视图 =====================

@login_required
def my_matrix_view(request):
    """个人培训矩阵 - 查看自己的培训要求和完成进度"""
    user = request.user

    # 获取用户所属部门的所有激活矩阵
    if user.department:
        matrices = TrainingMatrix.objects.filter(
            department=user.department,
            is_active=True
        ).prefetch_related(
            Prefetch('items', queryset=TrainingMatrixItem.objects.select_related('course').order_by('order', 'priority'))
        )
    else:
        matrices = TrainingMatrix.objects.none()

    # 构建矩阵数据
    matrix_data = []
    for matrix in matrices:
        items_data = []
        for item in matrix.items.all():
            # 检查岗位匹配（留空表示全员，或匹配用户职位）
            if item.position and item.position != user.position:
                continue

            # 获取用户进度
            try:
                progress = UserMatrixProgress.objects.get(
                    user=user, item=item
                )
                status = progress.status
                completed_at = progress.completed_at
                due_date = progress.due_date
                course_progress_pct = progress.course_progress.overall_progress if progress.course_progress else 0
            except UserMatrixProgress.DoesNotExist:
                # 自动创建进度记录
                due = timezone.now().date() + timedelta(days=item.required_months * 30)
                progress = UserMatrixProgress.objects.create(
                    user=user,
                    matrix=matrix,
                    item=item,
                    status='pending',
                    due_date=due,
                )
                status = 'pending'
                completed_at = None
                due_date = due
                course_progress_pct = 0

            # 检查课程实际进度
            try:
                cp = CourseProgress.objects.get(user=user, course=item.course)
                real_progress = cp.overall_progress
                is_completed = cp.is_completed
                if is_completed and status != 'completed':
                    progress.status = 'completed'
                    progress.completed_at = cp.completed_at or timezone.now()
                    progress.course_progress = cp
                    progress.save()
                    status = 'completed'
                    completed_at = progress.completed_at
            except CourseProgress.DoesNotExist:
                real_progress = 0
                is_completed = False

            items_data.append({
                'item': item,
                'status': status,
                'completed_at': completed_at,
                'due_date': due_date,
                'course_progress': max(real_progress, course_progress_pct),
                'is_completed': is_completed or status == 'completed',
            })

        if items_data:
            total = len(items_data)
            completed = sum(1 for i in items_data if i['is_completed'])
            matrix_data.append({
                'matrix': matrix,
                'items': items_data,
                'total': total,
                'completed': completed,
                'progress_pct': int(completed / total * 100) if total > 0 else 0,
            })

    # 统计数据
    total_required = sum(m['total'] for m in matrix_data)
    total_completed = sum(m['completed'] for m in matrix_data)

    return render(request, 'training_matrix/my_matrix.html', {
        'matrix_data': matrix_data,
        'total_required': total_required,
        'total_completed': total_completed,
        'overall_pct': int(total_completed / total_required * 100) if total_required > 0 else 0,
        'user': user,
    })