# Generated manually on 2026-07-23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgePoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='知识点名称')),
                ('description', models.TextField(blank=True, default='', verbose_name='描述')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='排序')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='question_bank.knowledgepoint', verbose_name='上级知识点')),
            ],
            options={
                'verbose_name': '知识点',
                'verbose_name_plural': '知识点',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='QuestionBank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField(verbose_name='题目内容')),
                ('question_type', models.CharField(choices=[('single_choice', '单选题'), ('multi_choice', '多选题'), ('true_false', '判断题'), ('fill_blank', '填空题'), ('essay', '简答题')], default='single_choice', max_length=20, verbose_name='题目类型')),
                ('option_a', models.CharField(blank=True, default='', max_length=500, verbose_name='选项A')),
                ('option_b', models.CharField(blank=True, default='', max_length=500, verbose_name='选项B')),
                ('option_c', models.CharField(blank=True, default='', max_length=500, verbose_name='选项C')),
                ('option_d', models.CharField(blank=True, default='', max_length=500, verbose_name='选项D')),
                ('correct_answer', models.TextField(verbose_name='正确答案')),
                ('analysis', models.TextField(blank=True, default='', help_text='题目解析，考生查看结果时可见', verbose_name='答案解析')),
                ('score', models.PositiveIntegerField(default=5, verbose_name='分值')),
                ('difficulty', models.CharField(choices=[('easy', '简单'), ('medium', '中等'), ('hard', '困难')], db_index=True, default='medium', max_length=10, verbose_name='难度')),
                ('tags', models.CharField(blank=True, default='', help_text='多个标签用逗号分隔，如：法规,安全,操作', max_length=500, verbose_name='标签')),
                ('usage_count', models.PositiveIntegerField(default=0, help_text='被引用到考试的次数', verbose_name='使用次数')),
                ('is_active', models.BooleanField(default=True, verbose_name='启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bank_questions', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
                ('knowledge_points', models.ManyToManyField(blank=True, related_name='questions', to='question_bank.knowledgepoint', verbose_name='知识点')),
            ],
            options={
                'verbose_name': '题库',
                'verbose_name_plural': '题库',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='questionbank',
            index=models.Index(fields=['question_type', 'difficulty'], name='question_bank_qtype_difficulty_idx'),
        ),
        migrations.AddIndex(
            model_name='questionbank',
            index=models.Index(fields=['is_active'], name='question_bank_active_idx'),
        ),
    ]