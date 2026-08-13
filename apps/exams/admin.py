"""
在线考试 - Admin配置
"""
from django.contrib import admin
from .models import Exam, Question, ExamAttempt, Answer, AnswerLog, PaperTemplate, PaperRule


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    ordering = ('order',)
    fields = ('question_text', 'question_type', 'option_a', 'option_b', 'option_c', 'option_d',
              'correct_answer', 'score', 'order')
    readonly_fields = ()


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration', 'total_score', 'pass_score', 'is_published', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_published', 'course', 'created_by')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'course')
        }),
        ('考试设置', {
            'fields': ('duration', 'total_score', 'pass_score', 'is_published')
        }),
        ('重考控制', {
            'fields': ('allow_retake', 'max_attempts', 'require_pass')
        }),
        ('系统信息', {
            'fields': ('created_by', 'exam_paper', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_type', 'question_text_preview', 'score', 'order')
    list_filter = ('question_type', 'exam')
    search_fields = ('question_text',)
    list_editable = ('score', 'order')

    def question_text_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_preview.short_description = '题目内容'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'user_answer', 'is_correct', 'score')
    fields = ('question', 'user_answer', 'is_correct', 'score')


class AnswerLogInline(admin.TabularInline):
    model = AnswerLog
    extra = 0
    readonly_fields = ('question', 'action_type', 'old_answer', 'new_answer', 'elapsed_seconds', 'ip_address', 'created_at')
    fields = ('question', 'action_type', 'old_answer', 'new_answer', 'elapsed_seconds', 'ip_address', 'created_at')
    ordering = ('created_at',)
    can_delete = False


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'status', 'score', 'is_passed', 'start_time', 'end_time', 'has_signature')
    list_filter = ('status', 'exam', 'is_passed')
    search_fields = ('user__username', 'user__last_name', 'exam__title')
    readonly_fields = ('start_time', 'end_time', 'score', 'is_passed')
    inlines = [AnswerInline, AnswerLogInline]

    def has_signature(self, obj):
        from apps.signatures.models import Signature
        return Signature.objects.filter(
            content_type__model='examattempt', object_id=obj.id
        ).exists()
    has_signature.short_description = '已签名'
    has_signature.boolean = True

    def has_change_permission(self, request, obj=None):
        """签名后的考试记录不可修改"""
        if obj and self.has_signature(obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """签名后的考试记录不可删除"""
        if obj and self.has_signature(obj):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'user_answer', 'is_correct', 'score')
    list_filter = ('is_correct', 'question__question_type')
    search_fields = ('user_answer',)

    def has_change_permission(self, request, obj=None):
        """已提交的答案不可修改"""
        return False

    def has_delete_permission(self, request, obj=None):
        """已提交的答案不可删除"""
        return False


@admin.register(AnswerLog)
class AnswerLogAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'action_type', 'old_answer_short', 'new_answer_short', 'elapsed_seconds', 'ip_address', 'created_at')
    list_filter = ('action_type', 'attempt__exam')
    search_fields = ('old_answer', 'new_answer')
    readonly_fields = ('attempt', 'question', 'old_answer', 'new_answer', 'action_type', 'elapsed_seconds', 'ip_address', 'created_at')

    def old_answer_short(self, obj):
        return obj.old_answer[:30] + '...' if len(obj.old_answer) > 30 else obj.old_answer or '-'
    old_answer_short.short_description = '变更前'

    def new_answer_short(self, obj):
        return obj.new_answer[:30] + '...' if len(obj.new_answer) > 30 else obj.new_answer or '-'
    new_answer_short.short_description = '变更后'

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PaperRuleInline(admin.TabularInline):
    model = PaperRule
    extra = 1
    fields = ('question_type', 'count', 'score_per_question', 'difficulty', 'knowledge_point_ids', 'order')


@admin.register(PaperTemplate)
class PaperTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'pass_score', 'is_active', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    inlines = [PaperRuleInline]
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.save()


@admin.register(PaperRule)
class PaperRuleAdmin(admin.ModelAdmin):
    list_display = ('template', 'question_type', 'count', 'score_per_question', 'difficulty', 'order')
    list_filter = ('template', 'question_type')
