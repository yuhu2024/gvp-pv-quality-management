"""
学习痕迹记录 - Admin配置
"""
from django.contrib import admin
from .models import LearningLog, OperationLog


@admin.register(LearningLog)
class LearningLogAdmin(admin.ModelAdmin):
    """学习记录Admin"""
    list_display = ('user', 'action_type', 'course', 'exam', 'material', 'duration', 'ip_address', 'created_at')
    search_fields = ('user__username', 'user__last_name', 'detail')
    list_filter = ('action_type', 'course', 'exam')
    readonly_fields = ('user', 'action_type', 'course', 'exam', 'material',
                       'detail', 'ip_address', 'user_agent', 'duration', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """操作日志Admin"""
    list_display = ('user', 'action', 'target_type', 'target_id', 'description', 'ip_address', 'created_at')
    search_fields = ('user__username', 'description')
    list_filter = ('action', 'target_type')
    readonly_fields = ('user', 'action', 'target_type', 'target_id',
                       'description', 'ip_address', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
