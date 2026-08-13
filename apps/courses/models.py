"""
课程资料管理 - 数据模型
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """课程分类"""
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='父分类'
    )
    name = models.CharField('分类名称', max_length=100)
    code = models.CharField('分类编码', max_length=50, unique=True, default='')
    description = models.TextField('分类描述', blank=True, default='')
    order = models.PositiveIntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '课程分类'
        verbose_name_plural = '课程分类'
        ordering = ['order', 'name']
        unique_together = [['parent', 'name']]

    def __str__(self):
        return self.name

    def get_children(self):
        """返回子分类"""
        return Category.objects.filter(parent=self, is_active=True)

    def get_full_path(self):
        """返回完整路径如 '技术部 > 安全培训 > 信息安全'"""
        parts = []
        current = self
        while current:
            parts.append(current.name)
            current = current.parent
        return ' > '.join(reversed(parts))


class Course(models.Model):
    """课程模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending_review', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
        ('published', '已发布'),
    ]

    title = models.CharField('课程标题', max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='课程分类'
    )
    description = models.TextField('课程描述', blank=True, default='')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_courses', verbose_name='创建者'
    )
    status = models.CharField(
        '状态', max_length=20, choices=STATUS_CHOICES, default='draft'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_courses', verbose_name='审核人'
    )
    review_note = models.TextField('审核意见', blank=True, default='')
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def can_be_published(self):
        """只有 approved 状态才能发布"""
        return self.status == 'approved'

    def publish(self):
        """设置 status 为 published，记录 published_at"""
        if self.can_be_published():
            self.status = 'published'
            self.published_at = timezone.now()
            self.save(update_fields=['status', 'published_at', 'updated_at'])


class CourseMaterial(models.Model):
    """课程资料/附件"""
    FILE_TYPE_CHOICES = [
        ('ppt', 'PPT课件'),
        ('word', 'Word文档'),
        ('pdf', 'PDF文档'),
        ('video', '视频'),
    ]

    MATERIAL_STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name='materials', verbose_name='所属课程'
    )
    title = models.CharField('资料标题', max_length=200)
    file_type = models.CharField('资料类型', max_length=20, choices=FILE_TYPE_CHOICES, default='pdf')
    file = models.FileField('资料文件', upload_to='courses/materials/%Y/%m/')
    file_size = models.PositiveIntegerField('文件大小（字节）', default=0)
    description = models.TextField('资料描述', blank=True, default='')
    upload_time = models.DateTimeField('上传时间', auto_now_add=True)
    download_count = models.PositiveIntegerField('下载次数', default=0)
    status = models.CharField(
        '审核状态', max_length=20, choices=MATERIAL_STATUS_CHOICES, default='approved'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='审核人'
    )
    review_note = models.TextField('审核意见', blank=True, default='')
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)

    class Meta:
        verbose_name = '课程资料'
        verbose_name_plural = '课程资料'
        ordering = ['-upload_time']

    def __str__(self):
        return f'{self.title} ({self.course.title})'

    def save(self, *args, **kwargs):
        # 自动计算文件大小
        if self.file:
            try:
                self.file_size = self.file.size
            except (OSError, ValueError):
                self.file_size = 0
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """格式化文件大小显示"""
        size = self.file_size
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        elif size < 1024 * 1024 * 1024:
            return f'{size / (1024 * 1024):.1f} MB'
        else:
            return f'{size / (1024 * 1024 * 1024):.1f} GB'

    @property
    def file_extension(self):
        """获取文件扩展名"""
        if self.file and self.file.name:
            import os
            return os.path.splitext(self.file.name)[1].lower()
        return ''


class CourseProgress(models.Model):
    """用户课程学习进度"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='course_progress', verbose_name='用户'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name='user_progress', verbose_name='课程'
    )

    # 视频进度
    video_progress = models.PositiveIntegerField('视频学习进度(%)', default=0)
    video_total_duration = models.PositiveIntegerField('视频总时长(秒)', default=0)
    video_watched_duration = models.PositiveIntegerField('已观看时长(秒)', default=0)

    # 资料学习
    materials_viewed = models.ManyToManyField(
        'CourseMaterial', blank=True, verbose_name='已查看资料'
    )

    # 整体进度
    overall_progress = models.PositiveIntegerField('整体进度(%)', default=0)
    is_completed = models.BooleanField('是否完成', default=False)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    # 综合成绩（由成绩权重计算）
    composite_score = models.DecimalField(
        '综合成绩', max_digits=5, decimal_places=2, null=True, blank=True
    )
    score_calculated_at = models.DateTimeField('成绩计算时间', null=True, blank=True)

    last_access_at = models.DateTimeField('最后访问时间', auto_now=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        unique_together = [['user', 'course']]
        verbose_name = '课程进度'
        verbose_name_plural = '课程进度'

    def __str__(self):
        return f'{self.user} - {self.course.title} ({self.overall_progress}%)'