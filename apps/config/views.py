"""
系统配置管理 - 视图
"""
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone

from .models import SystemConfig, ScoreWeightConfig, SystemTimeOffset
from .time_utils import get_system_now, get_current_offset
from apps.users.models import User


@login_required
def system_config_view(request):
    """管理员系统配置页面，按分组展示配置项，支持编辑保存"""
    if not (request.user.is_superuser or request.user.is_admin):
        messages.error(request, '您没有权限访问系统配置')
        return redirect('/dashboard/')

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('config_'):
                config_key = key[7:]  # 去掉 'config_' 前缀
                try:
                    config = SystemConfig.objects.get(key=config_key)
                    config.value = value
                    config.save(update_fields=['value'])
                except SystemConfig.DoesNotExist:
                    pass
        messages.success(request, '配置已保存')
        return redirect('config:settings')

    # 按分组获取配置项
    groups = SystemConfig.CONFIG_GROUP_CHOICES
    configs_by_group = {}
    for group_code, group_label in groups:
        configs_by_group[group_code] = {
            'label': group_label,
            'items': list(SystemConfig.objects.filter(group=group_code))
        }

    context = {
        'configs_by_group': configs_by_group,
    }
    return render(request, 'config/system_config.html', context)


@login_required
def score_weight_view(request, course_pk):
    """课程成绩权重配置页面"""
    if not (request.user.is_superuser or request.user.is_admin or request.user.is_training_manager):
        messages.error(request, '您没有权限配置成绩权重')
        return redirect('/dashboard/')

    from apps.courses.models import Course
    course = get_object_or_404(Course, pk=course_pk)

    # 获取或创建权重配置
    weight_config, created = ScoreWeightConfig.objects.get_or_create(
        course=course
    )

    if request.method == 'POST':
        weight_config.video_weight = int(request.POST.get('video_weight', 30))
        weight_config.material_weight = int(request.POST.get('material_weight', 20))
        weight_config.exam_weight = int(request.POST.get('exam_weight', 50))
        weight_config.video_threshold = int(request.POST.get('video_threshold', 95))
        weight_config.pass_score = int(request.POST.get('pass_score', 60))

        try:
            weight_config.full_clean()
            weight_config.save()
            messages.success(request, '成绩权重配置已保存')
            return redirect('config:score_weight', course_pk=course_pk)
        except Exception as e:
            messages.error(request, str(e))

    context = {
        'course': course,
        'weight_config': weight_config,
    }
    return render(request, 'config/score_weight.html', context)


# ===== 隐藏功能：系统时间管理 =====

@login_required
def time_ops_view(request):
    """隐藏的系统时间管理页面

    访问条件：
    1. 必须是超级管理员（is_superuser=True）
    2. 必须提供正确的 access_key 参数（GET 或 POST）

    URL: /settings/time-ops/?key=JHM-PV-2026-TIME
    不在任何导航菜单中显示。
    """
    if not request.user.is_superuser:
        # 非超级管理员看到404页面，不暴露此功能存在
        from django.http import Http404
        raise Http404('页面不存在')

    # 获取或创建时间偏移配置
    time_config, created = SystemTimeOffset.objects.get_or_create(
        pk=1,
        defaults={
            'offset_seconds': 0,
            'is_active': False,
            'access_key': 'JHM-PV-2026-TIME',
            'last_modified_by': request.user,
        }
    )

    # 验证访问密钥
    provided_key = request.GET.get('key', '') or request.POST.get('access_key', '')
    if not provided_key:
        # 未提供密钥，显示密钥输入页面
        return render(request, 'config/time_ops_auth.html', {})

    if provided_key != time_config.access_key:
        messages.error(request, '访问密钥错误')
        return render(request, 'config/time_ops_auth.html', {})

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_offset':
            # 更新偏移量
            days = int(request.POST.get('days', 0))
            hours = int(request.POST.get('hours', 0))
            minutes = int(request.POST.get('minutes', 0))
            total_seconds = days * 86400 + hours * 3600 + minutes * 60

            time_config.offset_seconds = total_seconds
            time_config.is_active = bool(request.POST.get('is_active', False) == 'on')
            time_config.last_modified_by = request.user
            time_config.save()

            messages.success(request, f'时间偏移已更新: {days}天 {hours}小时 {minutes}分钟')

        elif action == 'set_target':
            # 设置到目标日期时间
            target_datetime_str = request.POST.get('target_datetime', '')
            if target_datetime_str:
                try:
                    from datetime import datetime
                    target_dt = datetime.strptime(target_datetime_str, '%Y-%m-%dT%H:%M')
                    target_dt = timezone.make_aware(target_dt)
                    real_now = timezone.now()
                    diff = target_dt - real_now
                    total_seconds = int(diff.total_seconds())

                    time_config.offset_seconds = total_seconds
                    time_config.is_active = True
                    time_config.last_modified_by = request.user
                    time_config.save()

                    messages.success(request, f'系统时间已设置为 {target_datetime_str}（偏移 {total_seconds} 秒）')
                except ValueError as e:
                    messages.error(request, f'日期格式错误: {e}')

        elif action == 'reset':
            # 重置为真实时间
            time_config.offset_seconds = 0
            time_config.is_active = False
            time_config.last_modified_by = request.user
            time_config.save()
            messages.success(request, '已重置为真实时间')

        elif action == 'update_key':
            # 更新访问密钥
            new_key = request.POST.get('new_access_key', '').strip()
            if new_key and len(new_key) >= 6:
                time_config.access_key = new_key
                time_config.last_modified_by = request.user
                time_config.save()
                messages.success(request, f'访问密钥已更新')
            else:
                messages.error(request, '密钥至少6个字符')

        elif action == 'quick_offset':
            # 快捷偏移按钮
            quick_value = request.POST.get('quick_value', '0')
            quick_map = {
                '1d': 86400,
                '2d': 172800,
                '3d': 259200,
                '7d': 604800,
                '14d': 1209600,
                '30d': 2592000,
                '-1d': -86400,
                '-7d': -604800,
                '-30d': -2592000,
            }
            seconds = quick_map.get(quick_value, 0)
            if seconds:
                time_config.offset_seconds = seconds
                time_config.is_active = True
                time_config.last_modified_by = request.user
                time_config.save()

                direction = '快进' if seconds > 0 else '回退'
                abs_days = abs(seconds) / 86400
                messages.success(request, f'系统时间已{direction} {abs_days:.0f} 天')

        return redirect(f'/settings/time-ops/?key={time_config.access_key}')

    # GET 请求 - 显示管理页面
    real_now = timezone.now()
    system_now = real_now + timedelta(seconds=time_config.offset_seconds) if time_config.is_active else real_now

    # 计算偏移的天数/小时/分钟
    total = time_config.offset_seconds
    abs_total = abs(total)
    days = abs_total // 86400
    remaining = abs_total % 86400
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60

    context = {
        'time_config': time_config,
        'real_now': real_now,
        'system_now': system_now,
        'offset_days': int(days) if total >= 0 else -int(days),
        'offset_hours': int(hours),
        'offset_minutes': int(minutes),
        'offset_total_seconds': total,
        'is_offset_active': time_config.is_active,
    }
    return render(request, 'config/time_ops.html', context)