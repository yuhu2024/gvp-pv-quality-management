"""大模型管理 - Admin配置"""
from django.contrib import admin
from .models import LLMProvider, AIUsageLog


@admin.register(LLMProvider)
class LLMProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'model_name', 'temperature',
                    'is_active', 'is_default', 'created_at')
    list_filter = ('provider', 'is_active', 'is_default')
    search_fields = ('name', 'model_name', 'base_url')
    list_editable = ('is_active', 'is_default')


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = ('task_type', 'provider', 'is_success', 'total_tokens',
                    'duration_ms', 'created_by', 'created_at')
    list_filter = ('task_type', 'is_success', 'provider')
    search_fields = ('input_text', 'output_text', 'error_message')
    readonly_fields = ('provider', 'task_type', 'input_text', 'output_text',
                       'prompt_tokens', 'completion_tokens', 'total_tokens',
                       'duration_ms', 'is_success', 'error_message',
                       'created_by', 'created_at')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False