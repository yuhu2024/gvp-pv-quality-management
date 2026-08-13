"""
用户与账号管理 - Admin配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Department, Role, Permission


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """部门管理"""
    list_display = ('name', 'code', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('created_at',)
    ordering = ('name',)

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'description')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """角色管理"""
    list_display = ('name', 'code', 'description', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'description')
        }),
        ('权限配置', {
            'fields': ('permissions',)
        }),
    )

    readonly_fields = ('created_at',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """权限管理"""
    list_display = ('name', 'code', 'module', 'action', 'description')
    search_fields = ('name', 'code', 'description')
    list_filter = ('module', 'action')
    ordering = ('module', 'action')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ('employee_id', 'username', 'get_full_name', 'department', 'role', 'phone', 'is_active', 'date_joined')
    search_fields = ('username', 'employee_id', 'phone', 'last_name', 'first_name', 'email')
    list_filter = ('is_active', 'department', 'role', 'gender')
    ordering = ('-date_joined',)

    # 自定义列表显示字段
    def get_full_name(self, obj):
        return f'{obj.last_name}{obj.first_name}'
    get_full_name.short_description = '姓名'

    # 自定义fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('工号与部门', {
            'fields': ('employee_id', 'department', 'role', 'position')
        }),
        ('联系信息', {
            'fields': ('phone', 'gender', 'avatar')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # 只读字段
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')

    # 过滤器
    filter_horizontal = ()
