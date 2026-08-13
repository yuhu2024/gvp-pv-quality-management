"""
荣誉证书 - 视图
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse

from .models import CertificateTemplate, Certificate


@login_required
def certificate_list_view(request):
    """证书列表 - 管理员看全部，用户看自己的"""
    if request.user.is_superuser or request.user.is_admin:
        certificates = Certificate.objects.select_related('user', 'course', 'template').all()
    else:
        certificates = Certificate.objects.filter(
            user=request.user
        ).select_related('course', 'template')

    certificates = certificates.order_by('-issued_at')

    context = {
        'certificates': certificates,
    }
    return render(request, 'certificates/certificate_list.html', context)


@login_required
def certificate_detail_view(request, pk):
    """证书详情 - 渲染证书内容"""
    certificate = get_object_or_404(Certificate, pk=pk)

    # 权限检查：只有管理员或证书本人可以查看
    if not (request.user.is_superuser or request.user.is_admin or certificate.user == request.user):
        messages.error(request, '您没有权限查看此证书')
        return redirect('certificates:list')

    rendered_content = certificate.template.render(
        user=certificate.user,
        course=certificate.course,
        score=certificate.score,
        cert_no=certificate.cert_no,
    )

    context = {
        'certificate': certificate,
        'rendered_content': rendered_content,
    }
    return render(request, 'certificates/certificate_detail.html', context)


@login_required
def certificate_download_view(request, pk):
    """下载证书 - 返回格式化HTML供打印"""
    certificate = get_object_or_404(Certificate, pk=pk)

    # 权限检查
    if not (request.user.is_superuser or request.user.is_admin or certificate.user == request.user):
        messages.error(request, '您没有权限下载此证书')
        return redirect('certificates:list')

    if certificate.is_revoked:
        messages.error(request, '该证书已被撤销')
        return redirect('certificates:list')

    rendered_content = certificate.template.render(
        user=certificate.user,
        course=certificate.course,
        score=certificate.score,
        cert_no=certificate.cert_no,
    )

    html_content = f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>培训合格证书 - {certificate.cert_no}</title>
        <style>
            @media print {{
                body {{ margin: 0; padding: 40px; }}
                .no-print {{ display: none; }}
            }}
            body {{
                font-family: "SimSun", "宋体", serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                line-height: 1.8;
            }}
            .cert-container {{
                border: 3px double #b8860b;
                padding: 60px 40px;
                text-align: center;
                background: linear-gradient(135deg, #fffef5 0%, #fff8dc 100%);
                min-height: 600px;
            }}
            .cert-title {{
                font-size: 32px;
                font-weight: bold;
                color: #8b0000;
                margin-bottom: 40px;
                letter-spacing: 8px;
            }}
            .cert-content {{
                font-size: 18px;
                white-space: pre-wrap;
                text-align: left;
                padding: 20px 40px;
            }}
            .cert-footer {{
                margin-top: 40px;
                font-size: 14px;
                color: #666;
            }}
            .print-btn {{
                margin-bottom: 20px;
                padding: 10px 30px;
                font-size: 16px;
                background: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            .print-btn:hover {{ background: #40a9ff; }}
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="print-btn" onclick="window.print()">打印 / 导出PDF</button>
            <button class="print-btn" onclick="window.close()" style="background: #999;">关闭</button>
        </div>
        <div class="cert-container">
            <div class="cert-title">培训合格证书</div>
            <div class="cert-content">{rendered_content}</div>
            <div class="cert-footer">证书编号：{certificate.cert_no}</div>
        </div>
    </body>
    </html>
    '''

    return HttpResponse(html_content, content_type='text/html; charset=utf-8')


@login_required
def template_list_view(request):
    """证书模板列表 - 管理员"""
    if not (request.user.is_superuser or request.user.is_admin or request.user.is_training_manager):
        messages.error(request, '您没有权限访问此页面')
        return redirect('/dashboard/')

    templates = CertificateTemplate.objects.all().order_by('-created_at')

    context = {
        'templates': templates,
    }
    return render(request, 'certificates/template_list.html', context)


@login_required
def template_create_view(request):
    """创建证书模板"""
    if not (request.user.is_superuser or request.user.is_admin or request.user.is_training_manager):
        messages.error(request, '您没有权限创建证书模板')
        return redirect('/dashboard/')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        content_template = request.POST.get('content_template', '').strip()

        if not name:
            messages.error(request, '请输入模板名称')
        elif not content_template:
            messages.error(request, '请输入内容模板')
        else:
            template = CertificateTemplate.objects.create(
                name=name,
                description=description,
                content_template=content_template,
            )
            messages.success(request, f'证书模板"{template.name}"创建成功')
            return redirect('certificates:template_list')

    context = {
        'default_template': CertificateTemplate._meta.get_field('content_template').default,
    }
    return render(request, 'certificates/template_form.html', context)


@login_required
def template_edit_view(request, pk):
    """编辑证书模板"""
    if not (request.user.is_superuser or request.user.is_admin or request.user.is_training_manager):
        messages.error(request, '您没有权限编辑证书模板')
        return redirect('/dashboard/')

    template_obj = get_object_or_404(CertificateTemplate, pk=pk)

    if request.method == 'POST':
        template_obj.name = request.POST.get('name', '').strip()
        template_obj.description = request.POST.get('description', '').strip()
        template_obj.content_template = request.POST.get('content_template', '').strip()
        template_obj.is_active = 'is_active' in request.POST

        if not template_obj.name:
            messages.error(request, '请输入模板名称')
        elif not template_obj.content_template:
            messages.error(request, '请输入内容模板')
        else:
            template_obj.save()
            messages.success(request, f'证书模板"{template_obj.name}"已更新')
            return redirect('certificates:template_list')

    context = {
        'template': template_obj,
    }
    return render(request, 'certificates/template_form.html', context)


@login_required
def issue_certificate_view(request):
    """颁发证书 - 管理员选择课程+用户，自动生成"""
    if not (request.user.is_superuser or request.user.is_admin or request.user.is_training_manager):
        messages.error(request, '您没有权限颁发证书')
        return redirect('/dashboard/')

    from apps.courses.models import Course, CourseProgress
    from apps.users.models import User

    if request.method == 'POST':
        template_id = request.POST.get('template')
        course_id = request.POST.get('course')
        user_ids = request.POST.getlist('users')

        if not template_id or not course_id or not user_ids:
            messages.error(request, '请完整选择模板、课程和用户')
        else:
            template = get_object_or_404(CertificateTemplate, pk=template_id)
            course = get_object_or_404(Course, pk=course_id)
            issued_count = 0

            for uid in user_ids:
                user = get_object_or_404(User, pk=uid)

                # 检查是否已颁发
                if Certificate.objects.filter(user=user, course=course, is_revoked=False).exists():
                    messages.warning(request, f'用户 {user} 已拥有该课程的有效证书，已跳过')
                    continue

                # 获取成绩
                try:
                    progress = CourseProgress.objects.get(user=user, course=course)
                    score = progress.composite_score if progress.composite_score else 0
                except CourseProgress.DoesNotExist:
                    score = 0

                Certificate.objects.create(
                    template=template,
                    user=user,
                    course=course,
                    score=score,
                )
                issued_count += 1

            messages.success(request, f'成功颁发 {issued_count} 张证书')
            return redirect('certificates:list')

    # GET - 展示颁发表单
    templates = CertificateTemplate.objects.filter(is_active=True)
    courses = Course.objects.filter(status='published')

    context = {
        'templates': templates,
        'courses': courses,
    }
    return render(request, 'certificates/issue_certificate.html', context)