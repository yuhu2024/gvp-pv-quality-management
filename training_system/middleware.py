"""
中间件 - 强制修改密码
"""
from django.shortcuts import redirect
from django.urls import resolve


class ForcePasswordChangeMiddleware:
    """强制用户修改密码的中间件

    如果用户的 force_password_change 字段为 True，
    则重定向到修改密码页面，除非已经在该页面。
    """

    EXEMPT_URLS = [
        '/login/',
        '/logout/',
        '/change-password/',
        '/admin/',
        '/static/',
        '/media/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 仅对已登录用户检查
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None

        # 超级管理员不强制
        if request.user.is_superuser:
            return None

        # 检查是否需要强制修改密码
        if not getattr(request.user, 'force_password_change', False):
            return None

        # 检查当前路径是否在豁免列表中
        path = request.path_info
        for exempt_url in self.EXEMPT_URLS:
            if path.startswith(exempt_url):
                return None

        # API 请求返回 403
        if path.startswith('/api/'):
            from django.http import JsonResponse
            return JsonResponse({'error': '请先修改密码'}, status=403)

        # 重定向到修改密码页面
        from django.contrib import messages
        messages.warning(request, '请先修改您的初始密码后再继续操作。')
        return redirect('users:change_password')
