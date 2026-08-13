from django.contrib import admin
from .models import SystemConfig, ScoreWeightConfig


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['label', 'key', 'group', 'value_type', 'updated_at']
    list_filter = ['group', 'value_type']
    search_fields = ['key', 'label', 'description']
    list_editable = ['group', 'value_type']

    def save_model(self, request, obj, form, change):
        """记录系统配置变更到操作日志"""
        from apps.logs.models import OperationLog
        action = 'update' if change else 'create'
        old_value = None
        if change:
            try:
                old = SystemConfig.objects.get(pk=obj.pk)
                old_value = old.value
            except SystemConfig.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
        OperationLog.objects.create(
            user=request.user,
            action=action,
            target_type='SystemConfig',
            target_id=obj.id,
            description=f'{"修改" if change else "创建"}系统配置 [{obj.key}]: '
                        f'{"旧值=" + str(old_value) + ", " if old_value else ""}新值={obj.value}',
            ip_address=_get_client_ip(request),
        )


@admin.register(ScoreWeightConfig)
class ScoreWeightConfigAdmin(admin.ModelAdmin):
    list_display = ['course', 'video_weight', 'material_weight', 'exam_weight',
                    'video_threshold', 'pass_score', 'updated_at']
    list_filter = ['pass_score']
    search_fields = ['course__title']

    def save_model(self, request, obj, form, change):
        """记录成绩权重配置变更到操作日志"""
        from apps.logs.models import OperationLog
        action = 'update' if change else 'create'
        super().save_model(request, obj, form, change)
        OperationLog.objects.create(
            user=request.user,
            action=action,
            target_type='ScoreWeightConfig',
            target_id=obj.id,
            description=f'{"修改" if change else "创建"}成绩权重 [{obj.course.title}]: '
                        f'视频={obj.video_weight}%, 资料={obj.material_weight}%, 考试={obj.exam_weight}%',
            ip_address=_get_client_ip(request),
        )


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')