"""
题库管理 - 数据模型
"""
from django.db import models
from django.conf import settings


class KnowledgePoint(models.Model):
    """知识点 - 树形结构"""
    name = models.CharField('知识点名称', max_length=200)
    description = models.TextField('描述', blank=True, default='')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name='上级知识点'
    )
    order = models.PositiveIntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '知识点'
        verbose_name_plural = '知识点'
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} > {self.name}'
        return self.name

    @property
    def full_path(self):
        """获取完整路径"""
        if self.parent:
            return f'{self.parent.full_path} > {self.name}'
        return self.name


class QuestionBank(models.Model):
    """题库 - 独立于考试存储"""
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    QUESTION_TYPE_CHOICES = [
        ('single_choice', '单选题'),
        ('multi_choice', '多选题'),
        ('true_false', '判断题'),
        ('fill_blank', '填空题'),
        ('essay', '简答题'),
    ]

    question_text = models.TextField('题目内容')
    question_type = models.CharField(
        '题目类型', max_length=20,
        choices=QUESTION_TYPE_CHOICES, default='single_choice'
    )
    option_a = models.CharField('选项A', max_length=500, blank=True, default='')
    option_b = models.CharField('选项B', max_length=500, blank=True, default='')
    option_c = models.CharField('选项C', max_length=500, blank=True, default='')
    option_d = models.CharField('选项D', max_length=500, blank=True, default='')
    correct_answer = models.TextField('正确答案')
    analysis = models.TextField('答案解析', blank=True, default='', help_text='题目解析，考生查看结果时可见')
    score = models.PositiveIntegerField('分值', default=5)
    difficulty = models.CharField(
        '难度', max_length=10, choices=DIFFICULTY_CHOICES,
        default='medium', db_index=True
    )
    knowledge_points = models.ManyToManyField(
        KnowledgePoint, blank=True, related_name='questions', verbose_name='知识点'
    )
    tags = models.CharField('标签', max_length=500, blank=True, default='',
                            help_text='多个标签用逗号分隔，如：法规,安全,操作')
    usage_count = models.PositiveIntegerField('使用次数', default=0, help_text='被引用到考试的次数')
    is_active = models.BooleanField('启用', default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='bank_questions', verbose_name='创建者'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '题库'
        verbose_name_plural = '题库'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['question_type', 'difficulty']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        preview = self.question_text[:40]
        return f'[{self.get_difficulty_display()}] {preview}...' if len(self.question_text) > 40 else f'[{self.get_difficulty_display()}] {preview}'

    def get_options(self):
        """返回非空选项的字典"""
        options = {}
        if self.option_a:
            options['A'] = self.option_a
        if self.option_b:
            options['B'] = self.option_b
        if self.option_c:
            options['C'] = self.option_c
        if self.option_d:
            options['D'] = self.option_d
        return options

    def get_tag_list(self):
        """返回标签列表"""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def to_exam_question(self, exam, order):
        """将题库题目转换为考试题目"""
        from apps.exams.models import Question
        return Question.objects.create(
            exam=exam,
            question_text=self.question_text,
            question_type=self.question_type,
            option_a=self.option_a,
            option_b=self.option_b,
            option_c=self.option_c,
            option_d=self.option_d,
            correct_answer=self.correct_answer,
            score=self.score,
            order=order,
        )