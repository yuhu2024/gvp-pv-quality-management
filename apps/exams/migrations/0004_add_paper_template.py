# Generated manually on 2026-07-23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0003_add_exam_paper_and_answer_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaperTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='模板名称')),
                ('description', models.TextField(blank=True, default='', verbose_name='模板说明')),
                ('duration', models.PositiveIntegerField(default=60, verbose_name='考试时长（分钟）')),
                ('pass_score', models.PositiveIntegerField(default=60, verbose_name='及格分数')),
                ('is_active', models.BooleanField(default=True, verbose_name='启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='paper_templates', to='users.user', verbose_name='创建者')),
            ],
            options={
                'verbose_name': '出卷模板',
                'verbose_name_plural': '出卷模板',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PaperRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(choices=[('single_choice', '单选题'), ('multi_choice', '多选题'), ('true_false', '判断题'), ('fill_blank', '填空题'), ('essay', '简答题')], default='single_choice', max_length=20, verbose_name='题目类型')),
                ('count', models.PositiveIntegerField(default=10, verbose_name='题目数量')),
                ('score_per_question', models.PositiveIntegerField(default=5, verbose_name='每题分值')),
                ('difficulty', models.CharField(choices=[('easy', '简单'), ('medium', '中等'), ('hard', '困难'), ('mixed', '混合')], default='mixed', max_length=10, verbose_name='难度')),
                ('knowledge_point_ids', models.TextField(blank=True, default='', help_text='留空=不限知识点，填写知识点ID（逗号分隔）限定范围', verbose_name='知识点范围')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='排序')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rules', to='exams.papertemplate', verbose_name='所属模板')),
            ],
            options={
                'verbose_name': '出卷规则',
                'verbose_name_plural': '出卷规则',
                'ordering': ['order'],
            },
        ),
    ]