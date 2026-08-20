"""
系统配置管理 - 视图
"""
from datetime import timedelta, datetime
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db import transaction

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


# ===== 隐藏功能：单条培训记录时间修改 =====

# 记录类型注册表：模型 -> 可编辑的时间字段配置
RECORD_TYPE_CONFIG = {
    'course_progress': {
        'label': '课程学习进度',
        'model_path': 'apps.courses.models.CourseProgress',
        'fields': {
            'completed_at': {'label': '完成时间', 'bypass_auto': False},
            'score_calculated_at': {'label': '成绩计算时间', 'bypass_auto': False},
            'created_at': {'label': '创建时间', 'bypass_auto': True},
            'last_access_at': {'label': '最后访问时间', 'bypass_auto': True},
        },
        'display_fields': ['user', 'course', 'overall_progress', 'is_completed'],
        'order_field': '-completed_at',
    },
    'exam_attempt': {
        'label': '考试记录',
        'model_path': 'apps.exams.models.ExamAttempt',
        'fields': {
            'start_time': {'label': '开始时间', 'bypass_auto': True},
            'end_time': {'label': '结束时间', 'bypass_auto': False},
        },
        'display_fields': ['user', 'exam', 'score', 'is_passed', 'status'],
        'order_field': '-start_time',
    },
    'mandatory_trainee': {
        'label': '强制培训人员',
        'model_path': 'apps.plans.models.MandatoryTrainee',
        'fields': {
            'assigned_at': {'label': '分配时间', 'bypass_auto': True},
            'completed_at': {'label': '完成时间', 'bypass_auto': False},
        },
        'display_fields': ['user', 'plan', 'status', 'exam_attempts', 'last_exam_score'],
        'order_field': '-assigned_at',
    },
    'task_assignment': {
        'label': '任务分配',
        'model_path': 'apps.plans.models.TaskAssignment',
        'fields': {
            'assigned_at': {'label': '分配时间', 'bypass_auto': True},
            'completed_at': {'label': '完成时间', 'bypass_auto': False},
        },
        'display_fields': ['user', 'task', 'status', 'completion_duration'],
        'order_field': '-assigned_at',
    },
    'signature': {
        'label': '电子签名',
        'model_path': 'apps.signatures.models.Signature',
        'fields': {
            'signed_at': {'label': '签名时间', 'bypass_auto': True},
        },
        'display_fields': ['signed_by', 'signature_type', 'ip_address'],
        'order_field': '-signed_at',
    },
    'learning_log': {
        'label': '学习记录',
        'model_path': 'apps.logs.models.LearningLog',
        'fields': {
            'created_at': {'label': '记录时间', 'bypass_auto': True},
        },
        'display_fields': ['user', 'action_type', 'course', 'exam', 'detail'],
        'order_field': '-created_at',
    },
}


def _get_model_class(model_path):
    """动态导入模型类"""
    parts = model_path.rsplit('.', 1)
    module = __import__(parts[0], fromlist=[parts[1]])
    return getattr(module, parts[1])


def _parse_datetime_local(dt_str):
    """解析 datetime-local 格式的字符串为 aware datetime"""
    if not dt_str:
        return None
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M')
    return timezone.make_aware(dt)


def _format_datetime_local(dt):
    """格式化 datetime 为 datetime-local 格式"""
    if dt is None:
        return ''
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt.strftime('%Y-%m-%dT%H:%M')


def _verify_time_ops_access(request):
    """验证隐藏功能的访问权限，返回 (time_config, error_response_or_None)"""
    if not request.user.is_superuser:
        raise Http404('页面不存在')

    time_config, created = SystemTimeOffset.objects.get_or_create(
        pk=1,
        defaults={
            'offset_seconds': 0,
            'is_active': False,
            'access_key': 'JHM-PV-2026-TIME',
            'last_modified_by': request.user,
        }
    )

    provided_key = request.GET.get('key', '') or request.POST.get('access_key', '')
    if not provided_key:
        return time_config, 'auth_required'
    if provided_key != time_config.access_key:
        return time_config, 'auth_failed'
    return time_config, None


@login_required
def training_record_time_view(request):
    """隐藏功能：修改单条培训记录的时间，不影响其他记录

    访问条件与 time_ops 相同：超级管理员 + access_key
    URL: /settings/time-ops/records/?key=JHM-PV-2026-TIME
    """
    time_config, error = _verify_time_ops_access(request)
    access_key = time_config.access_key

    if error == 'auth_required':
        return render(request, 'config/time_ops_auth.html', {})
    if error == 'auth_failed':
        messages.error(request, '访问密钥错误')
        return render(request, 'config/time_ops_auth.html', {})

    # 处理 POST：修改单条记录的时间
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_record_time':
            record_type = request.POST.get('record_type', '')
            record_id = request.POST.get('record_id', '')
            field_name = request.POST.get('field_name', '')
            new_value_str = request.POST.get('new_value', '').strip()

            if record_type not in RECORD_TYPE_CONFIG:
                messages.error(request, '无效的记录类型')
                return redirect(f'/settings/time-ops/records/?key={access_key}')

            type_config = RECORD_TYPE_CONFIG[record_type]
            if field_name not in type_config['fields']:
                messages.error(request, '无效的时间字段')
                return redirect(f'/settings/time-ops/records/?key={access_key}')

            try:
                model_class = _get_model_class(type_config['model_path'])
                record = get_object_or_404(model_class, pk=record_id)

                field_config = type_config['fields'][field_name]
                old_value = getattr(record, field_name, None)

                # 解析新值
                if new_value_str:
                    new_value = _parse_datetime_local(new_value_str)
                else:
                    new_value = None

                # 保存旧值用于日志
                old_value_str = _format_datetime_local(old_value) if old_value else '空'

                # 对于 auto_now/auto_now_add 字段，使用 queryset.update() 绕过自动设置
                if field_config['bypass_auto']:
                    model_class.objects.filter(pk=record.pk).update(
                        **{field_name: new_value}
                    )
                else:
                    setattr(record, field_name, new_value)
                    record.save(update_fields=[field_name])

                # 记录操作日志
                from apps.logs.models import OperationLog
                new_value_display = _format_datetime_local(new_value) if new_value else '空'
                OperationLog.objects.create(
                    user=request.user,
                    action='update',
                    target_type='task',
                    target_id=record.pk,
                    description=(
                        f'修改时间字段: {type_config["label"]}#{record.pk}.{field_name} '
                        f'({field_config["label"]}) '
                        f'[{old_value_str} -> {new_value_display}]'
                    ),
                    ip_address=request.META.get('REMOTE_ADDR'),
                )

                messages.success(
                    request,
                    f'已修改 {type_config["label"]} #{record.pk} 的 '
                    f'{field_config["label"]}：{old_value_str} -> {new_value_display}'
                )

            except ValueError as e:
                messages.error(request, f'日期格式错误: {e}')
            except Exception as e:
                messages.error(request, f'修改失败: {e}')

            return redirect(f'/settings/time-ops/records/?key={access_key}&record_type={record_type}')

        elif action == 'batch_shift':
            # 批量时间偏移（仅选中的记录）
            record_type = request.POST.get('record_type', '')
            record_ids = request.POST.getlist('record_ids')
            field_name = request.POST.get('field_name', '')
            shift_days = int(request.POST.get('shift_days', 0))
            shift_hours = int(request.POST.get('shift_hours', 0))
            shift_minutes = int(request.POST.get('shift_minutes', 0))

            if record_type not in RECORD_TYPE_CONFIG:
                messages.error(request, '无效的记录类型')
                return redirect(f'/settings/time-ops/records/?key={access_key}')

            type_config = RECORD_TYPE_CONFIG[record_type]
            if field_name not in type_config['fields']:
                messages.error(request, '无效的时间字段')
                return redirect(f'/settings/time-ops/records/?key={access_key}')

            shift_delta = timedelta(
                days=shift_days, hours=shift_hours, minutes=shift_minutes
            )
            if shift_delta == timedelta():
                messages.warning(request, '未输入偏移量')
                return redirect(f'/settings/time-ops/records/?key={access_key}&record_type={record_type}')

            try:
                model_class = _get_model_class(type_config['model_path'])
                records = model_class.objects.filter(pk__in=record_ids)
                updated_count = 0

                for record in records:
                    current_val = getattr(record, field_name, None)
                    if current_val is None:
                        continue
                    if timezone.is_naive(current_val):
                        current_val = timezone.make_aware(current_val)
                    new_val = current_val + shift_delta

                    field_config = type_config['fields'][field_name]
                    if field_config['bypass_auto']:
                        model_class.objects.filter(pk=record.pk).update(
                            **{field_name: new_val}
                        )
                    else:
                        setattr(record, field_name, new_val)
                        record.save(update_fields=[field_name])
                    updated_count += 1

                # 记录日志
                from apps.logs.models import OperationLog
                direction = '快进' if shift_delta > timedelta() else '回退'
                OperationLog.objects.create(
                    user=request.user,
                    action='update',
                    target_type='task',
                    description=(
                        f'批量偏移时间: {type_config["label"]}.{field_name} '
                        f'共{updated_count}条记录 {direction} '
                        f'{abs(shift_days)}天{abs(shift_hours)}时{abs(shift_minutes)}分'
                    ),
                    ip_address=request.META.get('REMOTE_ADDR'),
                )

                messages.success(
                    request,
                    f'已批量{direction} {updated_count} 条记录的 '
                    f'{type_config["fields"][field_name]["label"]} '
                    f'({abs(shift_days)}天{abs(shift_hours)}时{abs(shift_minutes)}分)'
                )
            except Exception as e:
                messages.error(request, f'批量修改失败: {e}')

            return redirect(f'/settings/time-ops/records/?key={access_key}&record_type={record_type}')

    # GET 请求：显示记录列表
    record_type = request.GET.get('record_type', 'exam_attempt')
    if record_type not in RECORD_TYPE_CONFIG:
        record_type = 'exam_attempt'

    type_config = RECORD_TYPE_CONFIG[record_type]
    model_class = _get_model_class(type_config['model_path'])

    # 构建查询
    qs = model_class.objects.all()

    # 按用户筛选
    user_filter = request.GET.get('user_id', '').strip()
    if user_filter:
        user_field = 'user' if 'user' in [f.name for f in model_class._meta.get_fields()] else None
        if not user_field:
            # 尝试 signed_by 等
            for candidate in ['signed_by', 'user']:
                if candidate in [f.name for f in model_class._meta.get_fields()]:
                    user_field = candidate
                    break
        if user_field:
            qs = qs.filter(**{f'{user_field}_id': user_filter})

    # 按日期范围筛选
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    # 找到主要的时间字段用于日期过滤
    primary_time_field = list(type_config['fields'].keys())[0]
    if date_from:
        try:
            dt_from = timezone.make_aware(datetime.strptime(date_from, '%Y-%m-%d'))
            qs = qs.filter(**{f'{primary_time_field}__gte': dt_from})
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = timezone.make_aware(
                datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            )
            qs = qs.filter(**{f'{primary_time_field}__lt': dt_to})
        except ValueError:
            pass

    # 排序
    qs = qs.order_by(type_config.get('order_field', '-id'))

    # 获取所有用户列表用于筛选下拉框
    users = User.objects.filter(is_active=True).order_by('employee_id', 'last_name', 'first_name')

    # 分页
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # 为每条记录准备时间字段列表（有序，便于模板遍历）
    field_count = len(type_config['fields'])
    records_with_times = []
    for record in page_obj.object_list:
        time_field_list = []
        for field_name, field_config in type_config['fields'].items():
            val = getattr(record, field_name, None)
            time_field_list.append({
                'name': field_name,
                'label': field_config['label'],
                'value': val,
                'value_local': _format_datetime_local(val),
                'bypass_auto': field_config['bypass_auto'],
            })
        records_with_times.append({
            'record': record,
            'time_field_list': time_field_list,
        })

    context = {
        'time_config': time_config,
        'access_key': access_key,
        'record_type': record_type,
        'record_type_label': type_config['label'],
        'record_types': RECORD_TYPE_CONFIG,
        'type_config': type_config,
        'records_with_times': records_with_times,
        'field_count': field_count,
        'page_obj': page_obj,
        'users': users,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'config/time_ops_records.html', context)