"""
系统配置管理 - 数据模型
"""
import json

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class SystemConfig(models.Model):
    """系统配置"""
    CONFIG_GROUP_CHOICES = [
        ('general', '基础配置'),
        ('training', '培训配置'),
        ('exam', '考试配置'),
        ('certificate', '证书配置'),
        ('security', '安全配置'),
    ]

    group = models.CharField('配置分组', max_length=20, choices=CONFIG_GROUP_CHOICES)
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.TextField('配置值')
    value_type = models.CharField('值类型', max_length=20, choices=[
        ('string', '字符串'),
        ('integer', '整数'),
        ('float', '浮点数'),
        ('boolean', '布尔'),
        ('json', 'JSON'),
    ], default='string')
    label = models.CharField('配置标签', max_length=200)
    description = models.TextField('配置说明', blank=True, default='')
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['group', 'key']

    def __str__(self):
        return f'{self.label} ({self.key})'

    def get_value(self):
        if self.value_type == 'integer':
            return int(self.value)
        if self.value_type == 'float':
            return float(self.value)
        if self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        if self.value_type == 'json':
            return json.loads(self.value)
        return self.value

    @classmethod
    def get(cls, key, default=None):
        try:
            obj = cls.objects.get(key=key)
            return obj.get_value()
        except cls.DoesNotExist:
            return default


class ScoreWeightConfig(models.Model):
    """成绩权重配置"""
    course = models.OneToOneField(
        'courses.Course', on_delete=models.CASCADE,
        related_name='score_weight', verbose_name='课程'
    )
    video_weight = models.PositiveIntegerField(
        '视频学习进度权重(%)', default=30,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    material_weight = models.PositiveIntegerField(
        '资料学习权重(%)', default=20,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    exam_weight = models.PositiveIntegerField(
        '考试成绩权重(%)', default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    video_threshold = models.PositiveIntegerField(
        '视频完成阈值(%)', default=95,
        help_text='视频进度达到此值视为学完'
    )
    pass_score = models.PositiveIntegerField('及格分数', default=60)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '成绩权重配置'
        verbose_name_plural = '成绩权重配置'

    def __str__(self):
        return f'{self.course.title} - 成绩权重配置'

    def clean(self):
        if self.video_weight + self.material_weight + self.exam_weight != 100:
            raise ValidationError('三项权重之和必须等于100')


class SystemTimeOffset(models.Model):
    """系统时间偏移配置（隐藏功能）

    用于在后台调整系统显示/记录的时间。
    偏移量以秒为单位，正值表示时间快进，负值表示时间回退。
    只允许超级管理员通过隐藏URL访问。
    """
    offset_seconds = models.BigIntegerField(
        '时间偏移（秒）', default=0,
        help_text='正数=时间快进，负数=时间回退。如 86400=快进1天，-3600=回退1小时'
    )
    is_active = models.BooleanField('是否启用', default=False, help_text='关闭后系统使用真实时间')
    access_key = models.CharField(
        '访问密钥', max_length=128, default='JHM-PV-2026-TIME',
        help_text='隐藏页面的访问密钥，修改后需使用新密钥访问'
    )
    last_modified_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='最后修改人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '系统时间偏移'
        verbose_name_plural = '系统时间偏移'

    def __str__(self):
        status = '启用' if self.is_active else '关闭'
        return f'时间偏移({status}): {self.offset_seconds}秒'

    @classmethod
    def get_offset_seconds(cls):
        """获取当前偏移秒数（未配置或未启用则返回0）"""
        try:
            obj = cls.objects.first()
            if obj and obj.is_active:
                return obj.offset_seconds
        except Exception:
            pass
        return 0

    @classmethod
    def get_access_key(cls):
        """获取访问密钥"""
        try:
            obj = cls.objects.first()
            if obj:
                return obj.access_key
        except Exception:
            pass
        return 'JHM-PV-2026-TIME'