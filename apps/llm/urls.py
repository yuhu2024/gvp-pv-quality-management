"""大模型管理 - URL配置"""
from django.urls import path
from . import views

app_name = 'llm'

urlpatterns = [
    # 模型配置
    path('providers/', views.provider_list_view, name='providers'),
    path('providers/create/', views.provider_create_view, name='provider_create'),
    path('providers/<int:pk>/edit/', views.provider_edit_view, name='provider_edit'),
    path('providers/<int:pk>/delete/', views.provider_delete_view, name='provider_delete'),
    path('providers/<int:pk>/test/', views.provider_test_view, name='provider_test'),

    # AI 功能
    path('ai/questions/', views.ai_generate_questions_view, name='ai_questions'),
    path('ai/grade/<int:pk>/', views.ai_grade_view, name='ai_grade'),
    path('ai/course-summary/<int:pk>/', views.ai_course_summary_view, name='course_summary'),

    # 日志
    path('logs/', views.usage_logs_view, name='logs'),
]