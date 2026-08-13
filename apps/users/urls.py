"""
用户与账号管理 - URL配置
"""
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'users'

urlpatterns = [
    # 首页重定向到仪表盘
    path('', views.dashboard_view, name='home'),

    # 仪表盘
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # 个人资料
    path('profile/', views.profile_view, name='profile'),

    # 用户管理（管理员）
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/delete/<int:pk>/', views.user_delete_view, name='user_delete'),
    path('users/batch-import/', views.batch_import_view, name='batch_import'),

    # 登录/登出
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 修改密码
    path('change-password/', views.change_password_view, name='change_password'),

    # 密码重置
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            subject_template_name='registration/password_reset_subject.txt',
            email_template_name='registration/password_reset_email.html',
            success_url='/login/',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url='/login/',
        ),
        name='password_reset_confirm',
    ),
]
