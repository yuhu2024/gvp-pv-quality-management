"""
培训计划与任务分配 - 数据模型
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class TrainingPlan(models.Model):
    """培训计划（二级配置：关联基础配置中的课程分类、考试等）"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('expired', '已过期'),
    ]

    title = models.CharField('计划名称', max_length=200)
    description = models.TextField('计划描述', blank=True, default='')
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    deadline = models.DateField('培训截止日期', null=True, blank=True,
        help_text='所有参训人员必须在此日期前完成培训和考试')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')

    # 强制培训配置
    is_mandatory = models.BooleanField('是否强制培训', default=False,
        help_text='开启后，指定人员必须在时限内完成培训和考试')
    require_exam_pass = models.BooleanField('要求考试必须通过', default=True,
        help_text='开启后，考试不通过者需继续学习并重考，直到通过')
    allow_retake = models.BooleanField('允许重复考试', default=True,
        help_text='考核不通过时是否允许重新考试')
    max_attempts = models.PositiveIntegerField('最大考试次数', default=0,
        help_text='0=不限次数，考试不通过需重考直到通过或达到上限')

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_plans', verbose_name='创建者'
    )
    courses = models.ManyToManyField(
        'courses.Course', blank=True, related_name='training_plans', verbose_name='关联课程'
    )
    exams = models.ManyToManyField(
        'exams.Exam', blank=True, related_name='training_plans', verbose_name='关联考试'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '培训计划'
        verbose_name_plural = '培训计划'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        """检查培训是否已过期"""
        if self.deadline:
            return timezone.now().date() > self.deadline
        if self.end_date:
            return timezone.now().date() > self.end_date
        return False

    def get_mandatory_trainees(self):
        """获取强制培训名单"""
        return self.mandatory_trainees.all().select_related('user', 'user__department')


class MandatoryTrainee(models.Model):
    """强制培训人员名单"""
    STATUS_CHOICES = [
        ('pending', '未开始'),
        ('learning', '学习中'),
        ('exam_pending', '待考试'),
        ('passed', '已通过'),
        ('failed', '未通过（需重考）'),
        ('overdue', '已逾期'),
    ]

    plan = models.ForeignKey(
        TrainingPlan, on_delete=models.CASCADE,
        related_name='mandatory_trainees', verbose_name='所属培训计划'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='mandatory_trainings', verbose_name='参训人员'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    exam_attempts = models.PositiveIntegerField('考试次数', default=0)
    last_exam_score = models.PositiveIntegerField('最近考试得分', null=True, blank=True)
    remark = models.TextField('备注', blank=True, default='')

    class Meta:
        verbose_name = '强制培训人员'
        verbose_name_plural = '强制培训人员名单'
        ordering = ['assigned_at']
        unique_together = ('plan', 'user')

    def __str__(self):
        return f'{self.user} - {self.plan.title} ({self.get_status_display()})'

    def can_retake_exam(self):
        """检查是否可以重考"""
        if self.status == 'passed':
            return False
        if self.plan.max_attempts > 0 and self.exam_attempts >= self.plan.max_attempts:
            return False
        if self.plan.is_expired:
            return False
        return True

    def update_status_after_exam(self, score, is_passed):
        """考试后更新状态"""
        self.exam_attempts += 1
        self.last_exam_score = score
        if is_passed:
            self.status = 'passed'
            self.completed_at = timezone.now()
        elif self.plan.require_exam_pass:
            # 需要通过但未通过，标记为需重考
            if self.can_retake_exam():
                self.status = 'failed'
            else:
                self.status = 'overdue'
        else:
            # 不要求必须通过，标记完成
            self.status = 'passed'
            self.completed_at = timezone.now()
        self.save()


class PlanTask(models.Model):
    """计划任务"""
    TASK_TYPE_CHOICES = [
        ('course', '课程学习'),
        ('exam', '考试'),
        ('comprehensive', '综合'),
    ]

    plan = models.ForeignKey(
        TrainingPlan, on_delete=models.CASCADE,
        related_name='tasks', verbose_name='所属计划'
    )
    title = models.CharField('任务名称', max_length=200)
    task_type = models.CharField('任务类型', max_length=20, choices=TASK_TYPE_CHOICES, default='course')
    course = models.ForeignKey(
        'courses.Course', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='plan_tasks', verbose_name='关联课程'
    )
    exam = models.ForeignKey(
        'exams.Exam', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='plan_tasks', verbose_name='关联考试'
    )
    deadline = models.DateField('截止日期', null=True, blank=True)
    order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        verbose_name = '计划任务'
        verbose_name_plural = '计划任务'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.plan.title} - {self.title}'


class TaskAssignment(models.Model):
    """任务分配"""
    STATUS_CHOICES = [
        ('pending', '未开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('overdue', '已逾期'),
    ]

    task = models.ForeignKey(
        PlanTask, on_delete=models.CASCADE,
        related_name='assignments', verbose_name='任务'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='task_assignments', verbose_name='分配用户'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    completion_duration = models.PositiveIntegerField('完成用时（秒）', null=True, blank=True)

    class Meta:
        verbose_name = '任务分配'
        verbose_name_plural = '任务分配'
        ordering = ['assigned_at']
        unique_together = ('task', 'user')

    def __str__(self):
        return f'{self.user} - {self.task.title} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        # 当状态变为"已完成"时，自动记录完成时间和计算完成用时
        if self.status == 'completed' and self.completed_at is None:
            self.completed_at = timezone.now()
            if self.assigned_at:
                delta = self.completed_at - self.assigned_at
                self.completion_duration = int(delta.total_seconds())
        super().save(*args, **kwargs)
