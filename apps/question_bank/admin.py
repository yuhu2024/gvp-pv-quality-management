"""
题库管理 - Admin配置
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import KnowledgePoint, QuestionBank


@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order', 'question_count', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name',)
    list_editable = ('order',)
    ordering = ('parent__name', 'order', 'name')

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = '题目数'


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'question_type', 'difficulty', 'difficulty_badge',
                    'score', 'tag_list', 'usage_count', 'is_active', 'created_at')
    list_filter = ('question_type', 'difficulty', 'is_active', 'knowledge_points')
    search_fields = ('question_text', 'tags', 'correct_answer')
    list_editable = ('is_active', 'score', 'difficulty')
    filter_horizontal = ('knowledge_points',)

    fieldsets = (
        ('题目信息', {
            'fields': ('question_text', 'question_type', 'difficulty', 'score', 'is_active')
        }),
        ('选项与答案', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
        ('分类与解析', {
            'fields': ('knowledge_points', 'tags', 'analysis')
        }),
        ('元数据', {
            'fields': ('created_by', 'usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_by', 'usage_count', 'created_at', 'updated_at')

    def question_preview(self, obj):
        return obj.question_text[:60] + '...' if len(obj.question_text) > 60 else obj.question_text
    question_preview.short_description = '题目内容'

    def difficulty_badge(self, obj):
        colors = {'easy': 'green', 'medium': 'orange', 'hard': 'red'}
        return format_html(
            '<span style="background:#{};color:#fff;padding:2px 8px;border-radius:10px;font-size:0.8rem;">{}</span>',
            {'easy': '28a745', 'medium': 'fd7e14', 'hard': 'dc3545'}[obj.difficulty],
            obj.get_difficulty_display()
        )
    difficulty_badge.short_description = '难度'

    def tag_list(self, obj):
        tags = obj.get_tag_list()
        return format_html(
            ' '.join(f'<span style="background:#e9ecef;padding:1px 6px;border-radius:4px;font-size:0.75rem;">{t}</span>' for t in tags)
        )
    tag_list.short_description = '标签'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.save()