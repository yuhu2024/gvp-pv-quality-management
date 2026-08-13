"""
电子签名 - 视图
"""
import base64
import os
from io import BytesIO
from PIL import Image

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType

from .models import Signature


@login_required
def signature_pad_view(request):
    """
    签名板页面

    GET 参数：
        - type: 签名类型 ('exam' 或 'checkin')
        - target_type: 关联对象类型 (如 'examattempt', 'courseprogress')
        - target_id: 关联对象ID
        - redirect_url: 签名完成后的跳转地址
        - title: 页面标题（可选）
    """
    sig_type = request.GET.get('type', 'exam')
    target_type = request.GET.get('target_type', '')
    target_id = request.GET.get('target_id', '')
    redirect_url = request.GET.get('redirect_url', '/')
    title = request.GET.get('title', '电子签名确认')

    return render(request, 'signatures/signature_pad.html', {
        'sig_type': sig_type,
        'target_type': target_type,
        'target_id': target_id,
        'redirect_url': redirect_url,
        'page_title': title,
    })


@login_required
@require_POST
def save_signature_api(request):
    """
    AJAX API：保存签名图片

    POST 参数：
        - signature_data: Base64 编码的 PNG 图片数据 (data:image/png;base64,...)
        - signature_type: 'exam' 或 'checkin'
        - target_type: 关联对象类型 (可选)
        - target_id: 关联对象ID (可选)
    """
    signature_data = request.POST.get('signature_data', '')
    signature_type = request.POST.get('signature_type', 'exam')
    target_type = request.POST.get('target_type', '')
    target_id = request.POST.get('target_id', '')

    if not signature_data:
        return JsonResponse({'success': False, 'error': '签名数据不能为空'})

    # 解析 Base64 数据
    try:
        if ';base64,' in signature_data:
            header, base64_data = signature_data.split(';base64,')
        else:
            base64_data = signature_data
        image_data = base64.b64decode(base64_data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'签名数据解析失败：{str(e)}'})

    # 验证图片数据
    try:
        img = Image.open(BytesIO(image_data))
        if img.format != 'PNG':
            # 转换为 PNG
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            image_data = buffer.getvalue()
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'图片处理失败：{str(e)}'})

    # 创建签名记录
    sig = Signature(
        signed_by=request.user,
        signature_type=signature_type,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )

    # 关联对象
    if target_type and target_id:
        try:
            ct = ContentType.objects.get(model=target_type.lower())
            sig.content_type = ct
            sig.object_id = int(target_id)
        except (ContentType.DoesNotExist, ValueError):
            pass

    # 保存图片文件
    from django.core.files.base import ContentFile
    filename = f'sig_{request.user.id}_{int(timezone.now().timestamp())}.png'
    sig.signature_image.save(filename, ContentFile(image_data), save=True)

    return JsonResponse({
        'success': True,
        'signature_id': sig.id,
        'signed_at': sig.signed_at.strftime('%Y-%m-%d %H:%M:%S'),
        'image_url': sig.signature_image.url,
    })


@login_required
def signature_detail_view(request, pk):
    """查看签名详情"""
    sig = get_object_or_404(Signature, pk=pk)
    return render(request, 'signatures/signature_detail.html', {
        'signature': sig,
    })


def get_client_ip(request):
    """获取客户端真实 IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def checkin_qrcode_view(request, course_id):
    """生成课程签到二维码
    
    管理员/教师访问此页面，显示二维码供学员用微信扫描签到。
    二维码内容为签到页面的完整URL。
    """
    from apps.courses.models import Course
    course = get_object_or_404(Course, pk=course_id)
    
    # 构建签到URL（学员扫码后打开的页面）
    checkin_url = request.build_absolute_uri(
        reverse('signatures:mobile_checkin', args=[course_id])
    )
    
    return render(request, 'signatures/checkin_qrcode.html', {
        'course': course,
        'checkin_url': checkin_url,
    })


@login_required
def checkin_qrcode_image_view(request, course_id):
    """动态生成签到二维码图片（PNG）
    
    返回二维码PNG图片，可直接在<img>标签中显示。
    """
    import qrcode
    from django.http import HttpResponse
    from apps.courses.models import Course
    
    course = get_object_or_404(Course, pk=course_id)
    checkin_url = request.build_absolute_uri(
        reverse('signatures:mobile_checkin', args=[course_id])
    )
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(checkin_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 添加课程标题文字
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # qrcode 返回的是 PilImage 包装对象，转换为标准 PIL Image
    if hasattr(img, 'get_image'):
        qr_img = img.get_image()
    else:
        qr_img = img
    # 确保是 RGB 模式
    if qr_img.mode != 'RGB':
        qr_img = qr_img.convert('RGB')
    
    # 在二维码下方添加课程信息
    qr_width, qr_height = qr_img.size
    text_height = 60
    combined = Image.new('RGB', (qr_width, qr_height + text_height), 'white')
    combined.paste(qr_img, (0, 0))
    
    draw = ImageDraw.Draw(combined)
    # 尝试加载中文字体（支持 CJK 字符）
    font = None
    cjk_font_paths = [
        '/usr/share/fonts/opentype/noto-cjk-otf/NotoSansCJKsc-Regular.otf',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for fp in cjk_font_paths:
        try:
            font = ImageFont.truetype(fp, 16)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    
    title = course.title[:30] + ('...' if len(course.title) > 30 else '')
    text_width = draw.textlength(title, font=font)
    draw.text(
        ((qr_width - text_width) / 2, qr_height + 15),
        title,
        fill='black',
        font=font
    )
    
    buf = io.BytesIO()
    combined.save(buf, format='PNG')
    buf.seek(0)
    
    response = HttpResponse(buf.read(), content_type='image/png')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@login_required
def mobile_checkin_view(request, course_id):
    """手机端签到页面（微信扫码后打开）
    
    显示课程信息，引导用户进行手写签名签到。
    如果用户未登录，Django会自动重定向到登录页面。
    
    签名板完成签名后会携带 signature_id 参数返回本页面，
    本视图验证签名、关联学习进度、标记课程完成并记录日志。
    """
    from apps.courses.models import Course, CourseProgress
    
    course = get_object_or_404(Course, pk=course_id)
    progress, created = CourseProgress.objects.get_or_create(
        user=request.user, course=course
    )
    
    # 处理签名后的返回：验证签名并标记课程完成
    signature_id = request.GET.get('signature_id')
    if signature_id and not progress.is_completed:
        from apps.signatures.models import Signature
        from apps.logs.models import LearningLog
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
            
            # 记录学习日志（扫码签到类型）
            LearningLog.objects.create(
                user=request.user,
                action_type='checkin',
                course=course,
                detail=f'通过扫码完成课程《{course.title}》学习并电子签名确认（签名ID: {sig.id}）',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        except Signature.DoesNotExist:
            # 签名无效，继续显示签到页面引导用户重新签名
            pass
    
    # 检查是否已完成
    if progress.is_completed:
        from apps.signatures.models import Signature
        checkin_sig = Signature.objects.filter(
            content_type__model='courseprogress',
            object_id=progress.id,
            signature_type='checkin',
            signed_by=request.user
        ).first()
        
        return render(request, 'signatures/mobile_checkin_done.html', {
            'course': course,
            'progress': progress,
            'signature': checkin_sig,
        })
    
    # 构建签到完成后的回调URL
    from urllib.parse import urlparse, urlunparse
    current_url = request.build_absolute_uri()
    parsed = urlparse(current_url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    
    # 构建签名板URL
    sig_pad_url = reverse('signatures:pad')
    from urllib.parse import urlencode
    params = urlencode({
        'type': 'checkin',
        'target_type': 'courseprogress',
        'target_id': progress.id,
        'redirect_url': clean_url,
        'title': '培训签到签名确认',
    })
    full_sig_url = request.build_absolute_uri(f'{sig_pad_url}?{params}')
    
    return render(request, 'signatures/mobile_checkin.html', {
        'course': course,
        'progress': progress,
        'signature_pad_url': full_sig_url,
    })
