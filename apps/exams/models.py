"""
在线考试 - 数据模型
"""
from django.db import models
from django.conf import settings


class Exam(models.Model):
    """考试模型"""
    title = models.CharField('考试标题', max_length=200)
    description = models.TextField('考试说明', blank=True, default='')
    course = models.ForeignKey(
        'courses.Course', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='exams', verbose_name='关联课程'
    )
    duration = models.PositiveIntegerField('考试时长（分钟）', default=60)
    total_score = models.PositiveIntegerField('总分', default=100)
    pass_score = models.PositiveIntegerField('及格分数', default=60)
    is_published = models.BooleanField('是否发布', default=False)

    # 重考控制
    allow_retake = models.BooleanField('允许重复考试', default=True,
        help_text='关闭后，已通过的考试不能再次参加')
    max_attempts = models.PositiveIntegerField('最大考试次数', default=0,
        help_text='0=不限次数')
    require_pass = models.BooleanField('必须通过', default=False,
        help_text='开启后，未通过者需重考直到通过（配合培训计划的强制培训使用）')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_exams', verbose_name='创建者'
    )
    exam_paper = models.FileField('考试试卷', upload_to='exam_papers/%Y/%m/', blank=True, null=True, help_text='上传考试试卷（PDF/Word/PPT格式）')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '考试'
        verbose_name_plural = '考试'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """题目模型"""
    QUESTION_TYPE_CHOICES = [
        ('single_choice', '单选题'),
        ('multi_choice', '多选题'),
        ('true_false', '判断题'),
        ('fill_blank', '填空题'),
        ('essay', '简答题'),
    ]

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE,
        related_name='questions', verbose_name='所属考试'
    )
    question_text = models.TextField('题目内容')
    question_type = models.CharField('题目类型', max_length=20, choices=QUESTION_TYPE_CHOICES, default='single_choice')
    option_a = models.CharField('选项A', max_length=500, blank=True, default='')
    option_b = models.CharField('选项B', max_length=500, blank=True, default='')
    option_c = models.CharField('选项C', max_length=500, blank=True, default='')
    option_d = models.CharField('选项D', max_length=500, blank=True, default='')
    correct_answer = models.TextField('正确答案')
    score = models.PositiveIntegerField('分值', default=5)
    order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.exam.title} - 题目{self.order}'

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

    def check_answer(self, user_answer):
        """检查答案是否正确

        返回 (is_correct, score)
        对于简答题返回 (None, 0) 表示需要手动评分。
        """
        if not user_answer or not user_answer.strip():
            return False, 0

        user_answer = user_answer.strip()
        correct_answer = self.correct_answer.strip()

        if self.question_type == 'single_choice':
            return user_answer.upper() == correct_answer.upper(), self.score if user_answer.upper() == correct_answer.upper() else 0

        elif self.question_type == 'multi_choice':
            # 多选题：将答案按逗号分隔，排序后比较
            user_set = set(a.strip().upper() for a in user_answer.replace('，', ',').split(','))
            correct_set = set(a.strip().upper() for a in correct_answer.replace('，', ',').split(','))
            return user_set == correct_set, self.score if user_set == correct_set else 0

        elif self.question_type == 'true_false':
            return user_answer.lower() == correct_answer.lower(), self.score if user_answer.lower() == correct_answer.lower() else 0

        elif self.question_type == 'fill_blank':
            # 填空题：忽略大小写和首尾空格比较
            return user_answer.lower() == correct_answer.lower(), self.score if user_answer.lower() == correct_answer.lower() else 0

        elif self.question_type == 'essay':
            # 简答题：需要手动评分
            return None, 0

        return False, 0


class ExamAttempt(models.Model):
    """考试记录"""
    STATUS_CHOICES = [
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('timeout', '已超时'),
    ]

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE,
        related_name='attempts', verbose_name='考试'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='exam_attempts', verbose_name='考生'
    )
    score = models.PositiveIntegerField('得分', null=True, blank=True)
    is_passed = models.BooleanField('是否及格', null=True, blank=True)
    start_time = models.DateTimeField('开始时间', auto_now_add=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='in_progress')

    class Meta:
        verbose_name = '考试记录'
        verbose_name_plural = '考试记录'
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.user} - {self.exam.title} ({self.get_status_display()})'

    def is_timed_out(self):
        """检查考试是否已超时"""
        if self.status != 'in_progress':
            return False
        from django.utils import timezone
        elapsed = (timezone.now() - self.start_time).total_seconds() / 60
        return elapsed >= self.exam.duration

    def get_remaining_time(self):
        """获取剩余时间（秒）"""
        from django.utils import timezone
        if self.status != 'in_progress':
            return 0
        elapsed = (timezone.now() - self.start_time).total_seconds()
        remaining = self.exam.duration * 60 - elapsed
        return max(0, int(remaining))


class Answer(models.Model):
    """答题记录"""
    attempt = models.ForeignKey(
        ExamAttempt, on_delete=models.CASCADE,
        related_name='answers', verbose_name='考试记录'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='answers', verbose_name='题目'
    )
    user_answer = models.TextField('用户答案', blank=True, default='')
    is_correct = models.BooleanField('是否正确', null=True, blank=True)
    score = models.PositiveIntegerField('得分', null=True, blank=True)

    class Meta:
        verbose_name = '答题记录'
        verbose_name_plural = '答题记录'
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f'{self.attempt} - 题目{self.question.order}'


class AnswerLog(models.Model):
    """答题留痕 - 记录每次答案变更"""
    attempt = models.ForeignKey(
        ExamAttempt, on_delete=models.CASCADE,
        related_name='answer_logs', verbose_name='考试记录'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='answer_logs', verbose_name='题目'
    )
    old_answer = models.TextField('变更前答案', blank=True, default='')
    new_answer = models.TextField('变更后答案', blank=True, default='')
    action_type = models.CharField('操作类型', max_length=20, default='change',
        choices=[
            ('answer', '作答'),
            ('change', '修改'),
            ('delete', '清除'),
        ])
    elapsed_seconds = models.PositiveIntegerField('答题用时（秒）', default=0, help_text='从考试开始到本次作答的累计秒数')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    created_at = models.DateTimeField('记录时间', auto_now_add=True)

    class Meta:
        verbose_name = '答题留痕'
        verbose_name_plural = '答题留痕'
        ordering = ['attempt', 'question', 'created_at']

    def __str__(self):
        return f'{self.attempt} - Q{self.question.order} [{self.action_type}] {self.created_at.strftime("%H:%M:%S")}'


class PaperTemplate(models.Model):
    """出卷模板 - 定义自动出卷规则"""
    name = models.CharField('模板名称', max_length=200)
    description = models.TextField('模板说明', blank=True, default='')
    duration = models.PositiveIntegerField('考试时长（分钟）', default=60)
    pass_score = models.PositiveIntegerField('及格分数', default=60)
    is_active = models.BooleanField('启用', default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='paper_templates', verbose_name='创建者'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '出卷模板'
        verbose_name_plural = '出卷模板'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_rules(self):
        """获取出卷规则列表"""
        return self.rules.all().order_by('order')

    def generate_exam(self, title, created_by, course=None):
        """根据模板规则自动生成考试"""
        rules = self.get_rules()
        if not rules:
            raise ValueError('模板没有配置出卷规则')

        exam = Exam.objects.create(
            title=title,
            course=course,
            duration=self.duration,
            total_score=sum(r.total_score for r in rules),
            pass_score=self.pass_score,
            created_by=created_by,
        )

        order = 0
        for rule in rules:
            questions = rule.select_questions()
            for q in questions:
                order += 1
                exam_q = q.to_exam_question(exam, order)
                # 如果规则指定了分值，覆盖题库默认分值
                if rule.score_per_question:
                    exam_q.score = rule.score_per_question
                    exam_q.save()

            # 更新使用次数
            QuestionBank = q.__class__
            QuestionBank.objects.filter(
                id__in=[q.id for q in questions]
            ).update(usage_count=models.F('usage_count') + 1)

        # 更新考试总分
        exam.total_score = exam.questions.aggregate(s=models.Sum('score'))['s'] or exam.total_score
        exam.save(update_fields=['total_score'])

        return exam


class PaperRule(models.Model):
    """出卷规则 - 每类题目的数量和分值"""
    template = models.ForeignKey(
        PaperTemplate, on_delete=models.CASCADE,
        related_name='rules', verbose_name='所属模板'
    )
    question_type = models.CharField(
        '题目类型', max_length=20,
        choices=Question.QUESTION_TYPE_CHOICES, default='single_choice'
    )
    count = models.PositiveIntegerField('题目数量', default=10)
    score_per_question = models.PositiveIntegerField('每题分值', default=5)
    difficulty = models.CharField(
        '难度', max_length=10,
        choices=[('easy', '简单'), ('medium', '中等'), ('hard', '困难'), ('mixed', '混合')],
        default='mixed'
    )
    knowledge_point_ids = models.TextField(
        '知识点范围', blank=True, default='',
        help_text='留空=不限知识点，填写知识点ID（逗号分隔）限定范围'
    )
    order = models.PositiveIntegerField('排序', default=0)

    class Meta:
        verbose_name = '出卷规则'
        verbose_name_plural = '出卷规则'
        ordering = ['order']

    def __str__(self):
        return f'{self.template.name} - {self.get_question_type_display()} x{self.count}'

    @property
    def total_score(self):
        return self.count * self.score_per_question

    def select_questions(self):
        """根据规则从题库中随机抽题"""
        from apps.question_bank.models import QuestionBank
        qs = QuestionBank.objects.filter(
            question_type=self.question_type,
            is_active=True,
        )
        if self.difficulty != 'mixed':
            qs = qs.filter(difficulty=self.difficulty)
        if self.knowledge_point_ids:
            kp_ids = [int(x.strip()) for x in self.knowledge_point_ids.split(',') if x.strip()]
            if kp_ids:
                qs = qs.filter(knowledge_points__id__in=kp_ids).distinct()

        count = qs.count()
        if count < self.count:
            raise ValueError(
                f'题库中"{self.get_question_type_display()}"类型题目不足：'
                f'需要{self.count}题，实际只有{count}题'
            )

        # 随机抽取
        return list(qs.order_by('?')[:self.count])
