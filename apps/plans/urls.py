"""
培训计划与任务分配 - URL配置
"""
from django.urls import path

from . import views

app_name = 'plans'

urlpatterns = [
    path('', views.PlanListView.as_view(), name='list'),
    path('<int:pk>/', views.PlanDetailView.as_view(), name='detail'),
    path('create/', views.PlanCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.PlanEditView.as_view(), name='edit'),
    path('<int:pk>/assign/', views.assign_task_view, name='assign'),
    path('my-tasks/', views.my_tasks_view, name='my_tasks'),
    path('my-tasks/<int:pk>/complete/', views.complete_task_view, name='complete_task'),
    path('mandatory/', views.mandatory_training_overview, name='mandatory_overview'),
    path('<int:pk>/mandatory/', views.mandatory_trainee_manage, name='mandatory_trainee'),
]
