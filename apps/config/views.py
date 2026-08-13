"""
系统配置管理 - 视图
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View

from .models import SystemConfig, ScoreWeightConfig
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