"""
电子签名 - 后台管理
"""
from django.contrib import admin
from .models import Signature


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'signed_by', 'signature_type', 'signed_at', 'ip_address')
    list_filter = ('signature_type', 'signed_at')
    search_fields = ('signed_by__username', 'signed_by__employee_id')
    readonly_fields = ('signed_at', 'ip_address', 'user_agent')
    date_hierarchy = 'signed_at'

    def has_delete_permission(self, request, obj=None):
        """签名记录不可删除，确保审计追踪完整性"""
        return False
