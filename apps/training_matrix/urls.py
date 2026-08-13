"""
培训矩阵 - URL配置
"""
from django.urls import path
from . import views

app_name = 'training_matrix'

urlpatterns = [
    # 管理员/培训管理员 - 矩阵管理
    path('', views.matrix_list_view, name='list'),
    path('create/', views.matrix_create_view, name='create'),
    path('<int:pk>/', views.matrix_detail_view, name='detail'),
    path('<int:pk>/edit/', views.matrix_edit_view, name='edit'),
    path('<int:pk>/delete/', views.matrix_delete_view, name='delete'),
    path('<int:pk>/assign/', views.matrix_assign_view, name='assign'),
    path('<int:pk>/sync-progress/', views.matrix_sync_progress_view, name='sync_progress'),

    # 用户个人培训矩阵
    path('my/', views.my_matrix_view, name='my_matrix'),
]