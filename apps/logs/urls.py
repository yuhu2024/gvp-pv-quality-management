"""
学习痕迹记录 - URL配置
"""
from django.urls import path

from . import views

app_name = 'logs'

urlpatterns = [
    path('learning/', views.LearningLogView.as_view(), name='learning_log'),
    path('operation/', views.OperationLogView.as_view(), name='operation_log'),
    path('statistics/<int:user_id>/', views.user_statistics_view, name='user_statistics'),
    path('export/', views.export_learning_log_view, name='export_learning_log'),
    # 管理员统计面板
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    # 报表导出
    path('export/exam-scores/', views.export_exam_scores_view, name='export_exam_scores'),
    path('export/training-report/', views.export_training_report_view, name='export_training_report'),
]
