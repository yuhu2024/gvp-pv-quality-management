"""
学习痕迹记录 - 数据模型
"""
from django.db import models
from django.conf import settings


class LearningLog(models.Model):
    """学习痕迹记录"""
    ACTION_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('view_course', '查看课程'),
        ('download_material', '下载资料'),
        ('start_exam', '开始考试'),
        ('submit_exam', '提交考试'),
        ('complete_task', '完成任务'),
        ('checkin', '培训签到'),
        ('sign_exam', '考试签名'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='learning_logs', verbose_name='用户'
    )
    action_type = models.CharField('操作类型', max_length=30, choices=ACTION_CHOICES)
    course = models.ForeignKey(
        'courses.Course', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='learning_logs', verbose_name='关联课程'
    )
    exam = models.ForeignKey(
        'exams.Exam', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='learning_logs', verbose_name='关联考试'
    )
    material = models.ForeignKey(
        'courses.CourseMaterial', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='learning_logs', verbose_name='关联资料'
    )
    detail = models.TextField('详情描述', blank=True, default='')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.CharField('用户代理', max_length=500, blank=True, default='')
    duration = models.PositiveIntegerField('停留时长（秒）', null=True, blank=True)
    created_at = models.DateTimeField('记录时间', auto_now_add=True)

    class Meta:
        verbose_name = '学习记录'
        verbose_name_plural = '学习记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.get_action_type_display()} ({self.created_at})'


class OperationLog(models.Model):
    """操作日志"""
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('import', '导入'),
        ('export', '导出'),
        ('assign', '分配'),
    ]

    TARGET_TYPE_CHOICES = [
        ('user', '用户'),
        ('course', '课程'),
        ('exam', '考试'),
        ('plan', '计划'),
        ('task', '任务'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='operation_logs', verbose_name='操作用户'
    )
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    target_type = models.CharField('操作对象类型', max_length=20, choices=TARGET_TYPE_CHOICES, blank=True, default='')
    target_id = models.IntegerField('操作对象ID', null=True, blank=True)
    description = models.CharField('操作描述', max_length=500, blank=True, default='')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']

    def __str__(self):
        user_str = str(self.user) if self.user else '匿名'
        return f'{user_str} - {self.get_action_display()} {self.get_target_type_display()} ({self.created_at})'
