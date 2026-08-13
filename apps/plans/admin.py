"""
培训计划与任务分配 - Admin配置
"""
from django.contrib import admin
from .models import TrainingPlan, PlanTask, TaskAssignment


class PlanTaskInline(admin.TabularInline):
    """计划任务内联编辑"""
    model = PlanTask
    extra = 1
    ordering = ('order',)
    fields = ('title', 'task_type', 'course', 'exam', 'deadline', 'order')


class TaskAssignmentInline(admin.TabularInline):
    """任务分配内联编辑"""
    model = TaskAssignment
    extra = 0
    readonly_fields = ('assigned_at', 'completed_at', 'completion_duration')
    fields = ('user', 'status', 'assigned_at', 'completed_at', 'completion_duration')


@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    """培训计划Admin"""
    list_display = ('title', 'status', 'start_date', 'end_date', 'creator', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('status', 'creator')
    inlines = [PlanTaskInline]
    filter_horizontal = ('courses', 'exams')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'status', 'creator')
        }),
        ('时间设置', {
            'fields': ('start_date', 'end_date')
        }),
        ('关联资源', {
            'fields': ('courses', 'exams')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlanTask)
class PlanTaskAdmin(admin.ModelAdmin):
    """计划任务Admin"""
    list_display = ('title', 'plan', 'task_type', 'course', 'exam', 'deadline', 'order')
    search_fields = ('title', 'plan__title')
    list_filter = ('task_type', 'plan')
    list_editable = ('order',)
    inlines = [TaskAssignmentInline]


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    """任务分配Admin"""
    list_display = ('user', 'task', 'status', 'assigned_at', 'completed_at', 'completion_duration')
    search_fields = ('user__username', 'user__last_name', 'task__title')
    list_filter = ('status', 'task__plan', 'task__task_type')
    readonly_fields = ('assigned_at', 'completed_at', 'completion_duration')


from .models import MandatoryTrainee

@admin.register(MandatoryTrainee)
class MandatoryTraineeAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'exam_attempts', 'last_exam_score', 'assigned_at', 'completed_at')
    list_filter = ('status', 'plan')
    search_fields = ('user__username', 'user__last_name', 'user__first_name', 'plan__title')
    readonly_fields = ('assigned_at', 'completed_at', 'exam_attempts', 'last_exam_score')
