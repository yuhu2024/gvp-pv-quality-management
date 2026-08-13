"""
题库管理 - URL配置
"""
from django.urls import path
from . import views

app_name = 'question_bank'

urlpatterns = [
    # 题库
    path('', views.question_list_view, name='list'),
    path('create/', views.question_create_view, name='create'),
    path('<int:pk>/edit/', views.question_edit_view, name='edit'),
    path('<int:pk>/delete/', views.question_delete_view, name='delete'),
    path('batch-delete/', views.question_batch_delete_view, name='batch_delete'),
    path('export/', views.question_export_view, name='export'),
    path('import/', views.question_import_view, name='import'),
    path('stats/', views.question_stats_view, name='stats'),

    # 知识点
    path('knowledge-points/', views.knowledge_point_list_view, name='knowledge_points'),
    path('knowledge-points/create/', views.knowledge_point_create_view, name='kp_create'),
]