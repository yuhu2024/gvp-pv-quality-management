"""
培训矩阵 - 数据模型

培训矩阵 = 按部门配置的岗位/人员培训要求矩阵。
每个部门可配置一个培训矩阵，指定该部门各岗位/人员需要完成的课程列表。
每位学员可查看自己的培训矩阵，了解必修课程及完成进度。
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class TrainingMatrix(models.Model):
    """培训矩阵 - 按部门定义培训要求"""
    department = models.ForeignKey(
        'users.Department',
        on_delete=models.CASCADE,
        related_name='training_matrices',
        verbose_name='所属部门',
    )
    title = models.CharField('矩阵名称', max_length=200, help_text='如：药物警戒部培训矩阵')
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '培训矩阵'
        verbose_name_plural = '培训矩阵'
        ordering = ['department__name', 'title']
        unique_together = [['department', 'title']]

    def __str__(self):
        return f'{self.department.name} - {self.title}'

    def clean(self):
        if not self.department_id:
            raise ValidationError({'department': '请选择部门'})

    @property
    def total_items(self):
        return self.items.count()

    @property
    def position_count(self):
        """矩阵中定义的岗位数量"""
        return self.items.values('position').distinct().count()


class TrainingMatrixItem(models.Model):
    """培训矩阵条目 - 岗位/人员的课程要求"""
    PRIORITY_CHOICES = [
        (1, '高'),
        (2, '中'),
        (3, '低'),
    ]

    matrix = models.ForeignKey(
        TrainingMatrix,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='所属矩阵',
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='matrix_items',
        verbose_name='课程',
    )
    position = models.CharField(
        '岗位', max_length=100, blank=True, default='',
        help_text='指定岗位（留空表示部门全员必修）',
    )
    is_required = models.BooleanField('必修', default=True)
    required_months = models.PositiveIntegerField(
        '要求完成月数', default=3,
        help_text='入职/分配后要求完成的月数',
    )
    priority = models.IntegerField('优先级', choices=PRIORITY_CHOICES, default=2)
    order = models.PositiveIntegerField('排序', default=0)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '矩阵条目'
        verbose_name_plural = '矩阵条目'
        ordering = ['matrix', 'order', 'priority', 'id']
        unique_together = [['matrix', 'course', 'position']]

    def __str__(self):
        pos = f' [{self.position}]' if self.position else ' [全员]'
        required = '★' if self.is_required else '○'
        return f'{required}{self.course.title}{pos}'

    @property
    def position_display_name(self):
        return self.position if self.position else '全体人员'


class UserMatrixProgress(models.Model):
    """用户培训矩阵完成进度（缓存表，用于快速查询）"""
    STATUS_CHOICES = [
        ('pending', '未开始'),
        ('in_progress', '学习中'),
        ('completed', '已完成'),
        ('overdue', '已逾期'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matrix_progress',
        verbose_name='用户',
    )
    matrix = models.ForeignKey(
        TrainingMatrix,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='所属矩阵',
    )
    item = models.ForeignKey(
        TrainingMatrixItem,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='矩阵条目',
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    course_progress = models.ForeignKey(
        'courses.CourseProgress',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='matrix_progress_records',
        verbose_name='课程进度',
    )
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    due_date = models.DateField('截止日期', null=True, blank=True)

    class Meta:
        verbose_name = '用户矩阵进度'
        verbose_name_plural = '用户矩阵进度'
        ordering = ['user', 'matrix', 'item__order']
        unique_together = [['user', 'item']]
        indexes = [
            models.Index(fields=['user', 'matrix']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.item.course.title} [{self.get_status_display()}]'