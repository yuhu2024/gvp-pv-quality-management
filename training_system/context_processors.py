"""
全局 Context Processor - 为所有模板注入系统级变量
"""
from django.conf import settings


def system_settings(request):
    """注入系统名称等全局变量到模板上下文"""
    return {
        'SYSTEM_NAME': getattr(settings, 'SYSTEM_NAME', '君合盟药物警戒培训管理系统'),
        'SYSTEM_SHORT_NAME': getattr(settings, 'SYSTEM_SHORT_NAME', '君合盟PV培训系统'),
    }
