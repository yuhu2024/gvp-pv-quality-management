"""
学习排行榜 - 视图
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, Avg, Q, F, DurationField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from apps.logs.models import LearningLog
from apps.exams.models import ExamAttempt
from apps.courses.models import CourseProgress
from apps.users.models import Department


@login_required
def ranking_view(request):
    """学习排行榜页面"""
    tab = request.GET.get('tab', 'duration')  # duration / score / completion
    dept_id = request.GET.get('dept', '')
    period = request.GET.get('period', 'all')  # week / month / all

    # 构建时间范围过滤
    now = timezone.now()
    time_filter = Q()
    if period == 'week':
        week_start = now - timedelta(days=7)
        time_filter = Q(created_at__gte=week_start)
    elif period == 'month':
        month_start = now - timedelta(days=30)
        time_filter = Q(created_at__gte=month_start)

    # 部门过滤
    dept_filter = Q()
    if dept_id:
        dept_filter = Q(user__department_id=dept_id)

    rankings = []

    if tab == 'duration':
        # 学习时长榜：按总学习时长排名（从 LearningLog 聚合 duration）
        queryset = (
            LearningLog.objects
            .filter(time_filter, duration__isnull=False)
            .values('user__id', 'user__username', 'user__first_name', 'user__last_name',
                    'user__department__name', 'user__avatar')
            .annotate(
                total_duration=Coalesce(Sum('duration'), 0),
            )
            .order_by('-total_duration')[:50]
        )
        rankings = [
            {
                'rank': i + 1,
                'user_id': item['user__id'],
                'username': item['user__username'],
                'display_name': f"{item['user__last_name']}{item['user__first_name']}" or item['user__username'],
                'department': item['user__department__name'] or '未分配',
                'avatar': item['user__avatar'],
                'value': item['total_duration'],
                'value_display': _format_duration(item['total_duration']),
            }
            for i, item in enumerate(queryset)
        ]
        value_label = '学习时长'

    elif tab == 'score':
        # 考试成绩榜：按最高考试平均分排名
        queryset = (
            ExamAttempt.objects
            .filter(status='completed', score__isnull=False)
            .filter(time_filter)
            .values('user__id', 'user__username', 'user__first_name', 'user__last_name',
                    'user__department__name', 'user__avatar')
            .annotate(
                avg_score=Avg('score'),
                exam_count=Count('id'),
            )
            .order_by('-avg_score')[:50]
        )
        rankings = [
            {
                'rank': i + 1,
                'user_id': item['user__id'],
                'username': item['user__username'],
                'display_name': f"{item['user__last_name']}{item['user__first_name']}" or item['user__username'],
                'department': item['user__department__name'] or '未分配',
                'avatar': item['user__avatar'],
                'value': round(item['avg_score'], 1) if item['avg_score'] else 0,
                'value_display': f"{item['avg_score']:.1f} 分" if item['avg_score'] else '0 分',
                'extra': f'共 {item["exam_count"]} 次考试',
            }
            for i, item in enumerate(queryset)
        ]
        value_label = '平均成绩'

    elif tab == 'completion':
        # 课程完成榜：按已完成课程数排名
        queryset = (
            CourseProgress.objects
            .filter(is_completed=True)
            .filter(time_filter)
            .values('user__id', 'user__username', 'user__first_name', 'user__last_name',
                    'user__department__name', 'user__avatar')
            .annotate(
                completed_count=Count('id'),
            )
            .order_by('-completed_count')[:50]
        )
        rankings = [
            {
                'rank': i + 1,
                'user_id': item['user__id'],
                'username': item['user__username'],
                'display_name': f"{item['user__last_name']}{item['user__first_name']}" or item['user__username'],
                'department': item['user__department__name'] or '未分配',
                'avatar': item['user__avatar'],
                'value': item['completed_count'],
                'value_display': f'{item["completed_count"]} 门',
            }
            for i, item in enumerate(queryset)
        ]
        value_label = '完成课程数'

    # 获取部门列表供筛选
    departments = Department.objects.all().order_by('name')

    # 如果选择了部门，在前端过滤（因跨app聚合中部门过滤已在query中生效）
    if dept_id:
        rankings = [r for r in rankings if _filter_by_dept(r, dept_id)]

    # 重新编号
    for i, r in enumerate(rankings):
        r['rank'] = i + 1

    context = {
        'tab': tab,
        'dept_id': dept_id,
        'period': period,
        'departments': departments,
        'rankings': rankings,
        'value_label': value_label,
    }
    return render(request, 'ranking/ranking.html', context)


def _format_duration(seconds):
    """格式化秒数为可读时长"""
    if not seconds:
        return '0 分钟'
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f'{hours} 小时 {minutes} 分钟'
    return f'{minutes} 分钟'


def _filter_by_dept(ranking_item, dept_id):
    """根据部门名称筛选排行项"""
    from apps.users.models import Department
    try:
        dept = Department.objects.get(pk=dept_id)
        return ranking_item.get('department') == dept.name
    except Department.DoesNotExist:
        return True