"""
课程资料管理 - URL配置
"""
from django.urls import path

from . import views
from .admin_views import (
    CategoryListView, CategoryCreateView, CategoryEditView, CategoryDeleteView,
    admin_dashboard
)

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='detail'),
    path('create/', views.course_create_view, name='create'),
    path('<int:course_pk>/material/upload/', views.material_upload_view, name='material_upload'),
    path('<int:course_pk>/material/<int:pk>/delete/', views.material_delete_view, name='material_delete'),
    path('<int:course_pk>/material/<int:pk>/preview/', views.material_preview_view, name='material_preview'),
    path('<int:course_pk>/material/<int:pk>/download/', views.material_download_view, name='material_download'),
    # 审核相关路由
    path('review/', views.course_review_list_view, name='review_list'),
    path('<int:pk>/review/', views.course_review_view, name='review'),
    path('<int:pk>/publish/', views.course_publish_view, name='publish'),
    path('<int:pk>/checkin/', views.course_checkin_view, name='checkin'),
    path('material/<int:pk>/review/', views.material_review_view, name='material_review'),
    path('material/<int:pk>/video-progress/', views.update_video_progress, name='video_progress'),
    path('<int:pk>/generate-ppt/', views.generate_ppt_view, name='generate_ppt'),
]

urlpatterns += [
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('admin/categories/', CategoryListView.as_view(), name='admin_category_list'),
    path('admin/categories/create/', CategoryCreateView.as_view(), name='admin_category_create'),
    path('admin/categories/<int:pk>/edit/', CategoryEditView.as_view(), name='admin_category_edit'),
    path('admin/categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='admin_category_delete'),
]
