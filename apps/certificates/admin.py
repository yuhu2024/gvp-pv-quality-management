from django.contrib import admin
from .models import CertificateTemplate, Certificate


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['cert_no', 'user', 'course', 'score', 'issued_at', 'is_revoked']
    list_filter = ['is_revoked', 'issued_at']
    search_fields = ['cert_no', 'user__username', 'course__title']