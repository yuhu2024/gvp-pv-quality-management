"""
课程资料管理 - Admin配置
"""
from django.contrib import admin
from .models import Course, CourseMaterial, Category, CourseProgress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'order', 'is_active', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('is_active', 'parent')
    readonly_fields = ('created_at',)


class CourseMaterialInline(admin.TabularInline):
    model = CourseMaterial
    extra = 0
    readonly_fields = ('file_size', 'download_count', 'upload_time', 'status')
    fields = ('title', 'file_type', 'file', 'file_size', 'description', 'upload_time', 'download_count', 'status')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'creator', 'status', 'reviewer', 'published_at', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('status', 'category', 'creator')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at', 'published_at')
    inlines = [CourseMaterialInline]


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'file_type', 'file_size', 'status', 'download_count', 'upload_time')
    search_fields = ('title', 'course__title')
    list_filter = ('file_type', 'course', 'status')
    readonly_fields = ('file_size', 'download_count', 'upload_time', 'reviewed_at')


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'video_progress', 'overall_progress', 'is_completed', 'has_signature', 'composite_score', 'last_access_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('is_completed', 'course')
    readonly_fields = ('last_access_at', 'created_at', 'completed_at', 'score_calculated_at')

    def has_signature(self, obj):
        from apps.signatures.models import Signature
        return Signature.objects.filter(
            content_type__model='courseprogress', object_id=obj.id
        ).exists()
    has_signature.short_description = '已签名'
    has_signature.boolean = True

    def has_change_permission(self, request, obj=None):
        """签到签名后的学习进度不可修改"""
        if obj and self.has_signature(obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """签到签名后的学习进度不可删除"""
        if obj and self.has_signature(obj):
            return False
        return super().has_delete_permission(request, obj)
