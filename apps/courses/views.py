"""
课程资料管理 - 视图
"""
import os
import subprocess
import tempfile

from django.core.exceptions import ValidationError
from django.db import models as db_models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.utils.decorators import method_decorator
from django.http import Http404, FileResponse, JsonResponse
from django.conf import settings
from django.utils import timezone

from .models import Course, CourseMaterial, Category, CourseProgress
from apps.config.models import ScoreWeightConfig


def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_staff or user.is_superuser


# 文件上传安全配置
ALLOWED_UPLOAD_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx',
    '.mp4', '.avi', '.mov',
    '.mp3', '.wav',
    '.jpg', '.jpeg', '.png', '.gif',
    '.xls', '.xlsx',
}
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB


def validate_uploaded_file(file):
    """验证上传文件的安全性"""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationError(
            f'不支持的文件类型: {ext}。'
            f'允许的类型: {", ".join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}'
        )
    if file.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            f'文件过大（{file.size // 1024 // 1024}MB），最大允许 {MAX_UPLOAD_SIZE // 1024 // 1024}MB'
        )


# ==================== 课程视图 ====================

@method_decorator(login_required, name='dispatch')
class CourseListView(ListView):
    """课程列表 - 支持分类筛选和搜索"""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        # 管理员可以看到所有状态的课程，普通用户只看已发布的
        if user.is_staff or user.is_superuser:
            queryset = Course.objects.all()
        else:
            queryset = Course.objects.filter(status='published')

        category_id = self.request.GET.get('category')
        search = self.request.GET.get('search')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 传递分类树 context，支持多级分类筛选
        categories = Category.objects.all()
        context['categories'] = categories
        context['current_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('search', '')
        context['is_admin'] = self.request.user.is_staff or self.request.user.is_superuser
        return context


@method_decorator(login_required, name='dispatch')
class CourseDetailView(DetailView):
    """课程详情 - 显示所有资料及学习进度"""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Course.objects.all()
        return Course.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materials'] = self.object.materials.all()
        context['is_admin'] = self.request.user.is_staff or self.request.user.is_superuser

        # 获取用户学习进度
        progress, created = CourseProgress.objects.get_or_create(
            user=self.request.user, course=self.object
        )
        context['progress'] = progress

        # 获取签到签名（如果已完成）
        if progress.is_completed:
            from apps.signatures.models import Signature
            try:
                checkin_sig = Signature.objects.filter(
                    content_type__model='courseprogress',
                    object_id=progress.id,
                    signature_type='checkin'
                ).first()
                context['checkin_signature'] = checkin_sig
            except Exception:
                context['checkin_signature'] = None

        return context


@login_required
@user_passes_test(is_admin)
def course_create_view(request):
    """创建课程（管理员）"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        if not title:
            messages.error(request, '课程标题不能为空。')
            return render(request, 'courses/course_form.html', {
                'categories': Category.objects.all(),
            })

        course = Course.objects.create(
            title=title,
            description=description,
            category_id=category_id if category_id else None,
            creator=request.user,
            status='draft',
        )
        messages.success(request, f'课程 "{course.title}" 创建成功！')
        return redirect('courses:detail', pk=course.pk)

    return render(request, 'courses/course_form.html', {
        'categories': Category.objects.all(),
    })


# ==================== 课程资料视图 ====================

@login_required
@user_passes_test(is_admin)
def material_upload_view(request, course_pk):
    """上传课程资料（管理员）"""
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        file_type = request.POST.get('file_type', 'pdf')
        description = request.POST.get('description', '').strip()
        file = request.FILES.get('file')

        if not file:
            messages.error(request, '请选择要上传的文件。')
            return render(request, 'courses/material_upload.html', {
                'course': course,
                'file_type_choices': CourseMaterial.FILE_TYPE_CHOICES,
            })

        # 安全验证：检查文件类型和大小
        try:
            validate_uploaded_file(file)
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'courses/material_upload.html', {
                'course': course,
                'file_type_choices': CourseMaterial.FILE_TYPE_CHOICES,
            })

        material = CourseMaterial.objects.create(
            course=course,
            title=title or file.name,
            file_type=file_type,
            file=file,
            description=description,
        )
        messages.success(request, f'资料 "{material.title}" 上传成功！')
        return redirect('courses:detail', pk=course.pk)

    return render(request, 'courses/material_upload.html', {
        'course': course,
        'file_type_choices': CourseMaterial.FILE_TYPE_CHOICES,
    })


@login_required
@user_passes_test(is_admin)
def material_delete_view(request, course_pk, pk):
    """删除资料（管理员）"""
    material = get_object_or_404(CourseMaterial, pk=pk, course_id=course_pk)
    course = material.course

    if request.method == 'POST':
        material_name = material.title
        # 删除文件
        if material.file:
            try:
                material.file.delete(save=False)
            except (OSError, ValueError):
                pass
        material.delete()
        messages.success(request, f'资料 "{material_name}" 已删除。')
        return redirect('courses:detail', pk=course.pk)

    return render(request, 'courses/material_confirm_delete.html', {
        'material': material,
        'course': course,
    })


@login_required
def material_preview_view(request, course_pk, pk):
    """在线预览资料

    支持的预览方式：
    - PPT: 转图片展示（通过 LibreOffice 转换）
    - Word/PDF: 使用 PDF.js 在线查看
    - 视频: HTML5 video 播放器
    """
    material = get_object_or_404(CourseMaterial, pk=pk, course_id=course_pk)

    # 访问控制：非管理员只能预览已发布课程的资料
    if not (request.user.is_staff or request.user.is_superuser):
        if material.course.status != 'published':
            messages.error(request, '该课程资料尚未发布，无法预览。')
            return redirect('courses:detail', pk=course_pk)

    if not material.file:
        raise Http404('文件不存在')

    file_ext = material.file_extension.lower()
    context = {
        'material': material,
        'course': material.course,
        'file_url': material.file.url,
        'file_type': material.file_type,
        'file_ext': file_ext,
    }

    if material.file_type == 'video':
        # 视频文件 - 使用 HTML5 video 播放器
        template_name = 'courses/preview_video.html'
    elif material.file_type == 'pdf':
        # PDF 文件 - 使用 PDF.js 在线查看
        template_name = 'courses/preview_pdf.html'
    elif material.file_type == 'word':
        # Word 文件 - 先尝试转换为 PDF，再使用 PDF.js 查看
        # 如果无法转换，则提供下载
        pdf_path = _convert_office_to_pdf(material.file.path)
        if pdf_path:
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            context['pdf_url'] = f'{settings.MEDIA_URL}{relative_path}'
            template_name = 'courses/preview_pdf.html'
        else:
            template_name = 'courses/preview_unsupported.html'
    elif material.file_type == 'ppt':
        # PPT 文件 - 转换为图片展示
        images = _convert_ppt_to_images(material.file.path)
        if images:
            image_urls = []
            for img_path in images:
                relative_path = os.path.relpath(img_path, settings.MEDIA_ROOT)
                image_urls.append(f'{settings.MEDIA_URL}{relative_path}')
            context['slide_images'] = image_urls
            template_name = 'courses/preview_ppt.html'
        else:
            template_name = 'courses/preview_unsupported.html'
    else:
        template_name = 'courses/preview_unsupported.html'

    return render(request, template_name, context)


@login_required
def material_download_view(request, course_pk, pk):
    """下载课程资料并增加下载计数"""
    material = get_object_or_404(CourseMaterial, pk=pk, course_id=course_pk)

    # 访问控制：非管理员只能下载已发布课程的资料
    if not (request.user.is_staff or request.user.is_superuser):
        if material.course.status != 'published':
            messages.error(request, '该课程资料尚未发布，无法下载。')
            return redirect('courses:detail', pk=course_pk)

    if not material.file:
        raise Http404('文件不存在')

    # 增加下载计数
    CourseMaterial.objects.filter(pk=material.pk).update(
        download_count=db_models.F('download_count') + 1
    )

    response = FileResponse(
        material.file.open('rb'),
        as_attachment=True,
        filename=material.title + material.file_extension,
    )
    return response


# ==================== 辅助函数 ====================

# ==================== 审核相关视图 ====================

@login_required
@user_passes_test(is_admin)
def course_review_list_view(request):
    """待审核课程列表"""
    courses = Course.objects.filter(status='pending_review')
    return render(request, 'courses/review_list.html', {'courses': courses})


@login_required
@user_passes_test(is_admin)
def course_review_view(request, pk):
    """审核课程 - GET显示审核表单，POST处理审核"""
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')  # approve / reject
        note = request.POST.get('review_note', '')
        course.reviewer = request.user
        course.review_note = note
        course.reviewed_at = timezone.now()
        if action == 'approve':
            course.status = 'approved'
        elif action == 'reject':
            course.status = 'rejected'
        course.save()
        messages.success(request, f'课程已{"通过" if action == "approve" else "拒绝"}审核')
        return redirect('courses:review_list')
    return render(request, 'courses/review_form.html', {'course': course})


@login_required
@user_passes_test(is_admin)
def course_publish_view(request, pk):
    """发布课程"""
    course = get_object_or_404(Course, pk=pk)
    if course.status == 'approved':
        course.status = 'published'
        course.published_at = timezone.now()
        course.save()
        messages.success(request, '课程已发布')
    return redirect('courses:detail', pk=pk)


@login_required
@user_passes_test(is_admin)
def material_review_view(request, pk):
    """审核资料"""
    material = get_object_or_404(CourseMaterial, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        note = request.POST.get('review_note', '')
        material.status = 'approved' if action == 'approve' else 'rejected'
        material.reviewer = request.user
        material.review_note = note
        material.reviewed_at = timezone.now()
        material.save()
        messages.success(request, f'资料已{"通过" if action == "approve" else "拒绝"}审核')
        return redirect('courses:detail', pk=material.course.pk)
    return render(request, 'courses/material_review.html', {'material': material})


@login_required
@require_POST
def update_video_progress(request, material_pk):
    """更新视频观看进度 - 防作弊"""
    import json
    material = get_object_or_404(CourseMaterial, pk=material_pk, file_type='video')
    data = json.loads(request.body)
    watched_seconds = int(data.get('watched_seconds', 0))
    total_seconds = int(data.get('total_seconds', 0))

    progress, created = CourseProgress.objects.get_or_create(
        user=request.user, course=material.course
    )

    # 防作弊：累加观看时长，不超过总时长
    if watched_seconds > progress.video_watched_duration:
        # 限制单次上报跳跃不超过30秒（防止直接拖到末尾）
        if progress.video_watched_duration > 0:
            max_jump = 30
            watched_seconds = min(watched_seconds, progress.video_watched_duration + max_jump)

        # 不超过总时长的95%（由系统配置的阈值控制）
        threshold = int(ScoreWeightConfig.objects.filter(course=material.course).values_list('video_threshold', flat=True).first() or 95)
        max_allowed = int(total_seconds * threshold / 100)
        watched_seconds = min(watched_seconds, max_allowed)

        progress.video_watched_duration = watched_seconds
        progress.video_total_duration = total_seconds
        if total_seconds > 0:
            progress.video_progress = min(int(watched_seconds / total_seconds * 100), 100)

        # 检查是否完成
        if progress.video_progress >= threshold:
            progress.is_completed = True
            if not progress.completed_at:
                progress.completed_at = timezone.now()

        progress.save()

    return JsonResponse({
        'progress': progress.video_progress,
        'is_completed': progress.is_completed,
        'threshold': threshold
    })

@login_required
def course_checkin_view(request, pk):
    """课程签到确认 - 学习完成后签名确认

    流程：
    1. 用户点击"确认完成并签到"，跳转到签名页面
    2. 签名后返回到本视图（GET 带 signature_id）
    3. 验证签名，标记课程完成，记录学习日志
    """
    from apps.signatures.models import Signature
    from apps.logs.models import LearningLog

    course = get_object_or_404(Course, pk=pk)
    progress, created = CourseProgress.objects.get_or_create(
        user=request.user, course=course
    )

    # 检查是否已完成
    if progress.is_completed:
        messages.info(request, '您已完成本课程的学习签到。')
        return redirect('courses:detail', pk=pk)

    # 处理签名后的返回
    signature_id = request.GET.get('signature_id')
    if signature_id:
        try:
            sig = Signature.objects.get(
                id=signature_id,
                signed_by=request.user,
                signature_type='checkin'
            )
            # 关联签名到学习进度
            sig.content_object = progress
            sig.save()

            # 标记课程完成
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.overall_progress = 100
            progress.save()

            # 记录学习日志（签到类型）
            LearningLog.objects.create(
                user=request.user,
                action_type='checkin',
                course=course,
                detail=f'完成课程《{course.title}》学习并电子签名确认（签名ID: {sig.id}）',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )

            messages.success(
                request,
                f'恭喜！您已完成《{course.title}》的学习签到，签名时间：{sig.signed_at.strftime("%Y-%m-%d %H:%M:%S")}'
            )
            return redirect('courses:detail', pk=pk)

        except Signature.DoesNotExist:
            messages.error(request, '签名无效或不存在，请重新签名。')

    # 未签名或签名无效：显示确认页面，引导去签名
    # 使用不带 query string 的 URL 作为 redirect_url，防止携带旧 signature_id
    from urllib.parse import urlparse, urlunparse
    current_url = request.build_absolute_uri()
    parsed = urlparse(current_url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    return render(request, 'courses/checkin_confirm.html', {
        'course': course,
        'progress': progress,
        'clean_checkin_url': clean_url,
    })


def get_client_ip(request):
    """获取客户端真实 IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _convert_office_to_pdf(file_path):
    """使用 LibreOffice 将 Office 文件转换为 PDF

    返回转换后的 PDF 文件路径，失败返回 None。
    """
    try:
        output_dir = os.path.join(settings.MEDIA_ROOT, 'previews', 'pdf')
        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        pdf_output = os.path.join(output_dir, f'{base_name}.pdf')

        # 检查是否已缓存
        if os.path.exists(pdf_output):
            return pdf_output

        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            file_path,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)

        if result.returncode == 0 and os.path.exists(pdf_output):
            return pdf_output
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


# ==================== PPT 自动生成 ====================

@login_required
@user_passes_test(is_admin)
def generate_ppt_view(request, pk):
    """为课程自动生成 PPT 课件"""
    course = get_object_or_404(Course, pk=pk)
    materials = course.materials.all()

    if not materials.exists():
        messages.warning(request, '课程暂无资料，请先上传资料后再生成 PPT。')
        return redirect('courses:detail', pk=course.pk)

    from .ppt_generator import generate_course_ppt

    try:
        file_path, file_name = generate_course_ppt(course, materials)
    except Exception as e:
        messages.error(request, f'PPT 生成失败：{e}')
        return redirect('courses:detail', pk=course.pk)

    if file_path is None:
        messages.error(request, file_name)  # file_name is the error message
        return redirect('courses:detail', pk=course.pk)

    # 返回文件下载
    response = FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=file_name,
        content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )
    return response


def _convert_ppt_to_images(file_path):
    """使用 LibreOffice 将 PPT 转换为图片

    返回图片路径列表，失败返回 None。
    """
    try:
        output_dir = os.path.join(settings.MEDIA_ROOT, 'previews', 'slides')
        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        slide_output_dir = os.path.join(output_dir, base_name)
        os.makedirs(slide_output_dir, exist_ok=True)

        # 检查是否已缓存
        existing_images = sorted([
            os.path.join(slide_output_dir, f)
            for f in os.listdir(slide_output_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
        if existing_images:
            return existing_images

        # 先转为 PDF
        pdf_path = _convert_office_to_pdf(file_path)
        if not pdf_path:
            return None

        # 使用 pdftoppm 将 PDF 转为图片
        cmd = [
            'pdftoppm',
            '-png',
            '-r', '150',
            pdf_path,
            os.path.join(slide_output_dir, base_name),
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=120)

        if result.returncode == 0:
            images = sorted([
                os.path.join(slide_output_dir, f)
                for f in os.listdir(slide_output_dir)
                if f.lower().endswith('.png')
            ])
            return images if images else None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None
