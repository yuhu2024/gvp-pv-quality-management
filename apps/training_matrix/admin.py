"""
培训矩阵 - 管理后台配置
"""
from django.contrib import admin
from .models import TrainingMatrix, TrainingMatrixItem, UserMatrixProgress


class TrainingMatrixItemInline(admin.TabularInline):
    model = TrainingMatrixItem
    extra = 3
    fields = ['course', 'position', 'is_required', 'required_months', 'priority', 'order']
    autocomplete_fields = ['course']
    ordering = ['order', 'priority']


@admin.register(TrainingMatrix)
class TrainingMatrixAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'is_active', 'total_items', 'position_count', 'updated_at']
    list_filter = ['is_active', 'department']
    search_fields = ['title', 'department__name', 'description']
    inlines = [TrainingMatrixItemInline]
    ordering = ['department__name', 'title']


@admin.register(TrainingMatrixItem)
class TrainingMatrixItemAdmin(admin.ModelAdmin):
    list_display = ['course', 'matrix', 'position_display_name', 'is_required', 'required_months', 'priority']
    list_filter = ['is_required', 'matrix__department']
    search_fields = ['course__title', 'position', 'matrix__title']
    autocomplete_fields = ['course', 'matrix']


@admin.register(UserMatrixProgress)
class UserMatrixProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'matrix', 'item', 'status', 'due_date', 'completed_at']
    list_filter = ['status', 'matrix__department']
    search_fields = ['user__username', 'user__last_name', 'user__first_name']
    date_hierarchy = 'assigned_at'