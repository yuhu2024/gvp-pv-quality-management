"""
在线考试 - URL配置
"""
from django.urls import path

from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.ExamListView.as_view(), name='list'),
    path('<int:pk>/', views.exam_detail_view, name='detail'),
    path('create/', views.exam_create_view, name='create'),
    path('<int:pk>/take/', views.take_exam_view, name='take'),
    path('<int:pk>/result/', views.exam_result_view, name='result'),
    path('<int:pk>/scores/', views.exam_score_view, name='scores'),
    path('attempt/<int:pk>/logs/', views.exam_attempt_log_view, name='attempt_logs'),
    path('attempt/<int:attempt_pk>/answer-log/', views.answer_log_api, name='answer_log_api'),

    # 自动出卷
    path('paper-templates/', views.paper_template_list_view, name='paper_template_list'),
    path('paper-templates/create/', views.paper_template_create_view, name='paper_template_create'),
    path('paper-templates/<int:pk>/edit/', views.paper_template_edit_view, name='paper_template_edit'),
    path('paper-templates/<int:pk>/delete/', views.paper_template_delete_view, name='paper_template_delete'),
    path('paper-templates/<int:pk>/generate/', views.paper_generate_view, name='paper_generate'),
]