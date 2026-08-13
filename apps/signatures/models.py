"""
电子签名 - 数据模型
支持考试签名和培训签到签名
"""
import os
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


def signature_upload_path(instance, filename):
    """签名图片存储路径：signatures/YYYY/MM/UUID.png"""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg']:
        ext = '.png'
    return f'signatures/{timezone.now().strftime("%Y/%m")}/{uuid.uuid4().hex}{ext}'


class Signature(models.Model):
    """电子签名记录"""
    SIGNATURE_TYPE_CHOICES = [
        ('exam', '考试签名'),
        ('checkin', '培训签到'),
    ]

    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='signatures', verbose_name='签名者'
    )
    signature_type = models.CharField(
        '签名类型', max_length=20, choices=SIGNATURE_TYPE_CHOICES, default='exam'
    )
    signature_image = models.ImageField(
        '签名图片', upload_to=signature_upload_path
    )
    signed_at = models.DateTimeField('签名时间', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.CharField('设备信息', max_length=500, blank=True, default='')

    # GenericForeignKey 支持关联到任意对象（ExamAttempt / CourseProgress）
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        null=True, blank=True, verbose_name='关联对象类型'
    )
    object_id = models.PositiveIntegerField('关联对象ID', null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = '电子签名'
        verbose_name_plural = '电子签名'
        ordering = ['-signed_at']
        indexes = [
            models.Index(fields=['signed_by', 'signature_type']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'{self.signed_by} - {self.get_signature_type_display()} ({self.signed_at.strftime("%Y-%m-%d %H:%M")})'
