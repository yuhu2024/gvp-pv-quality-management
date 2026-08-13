# Generated manually on 2026-07-22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0002_initial'),
    ]

    operations = [
        # 给 Exam 添加 exam_paper 字段
        migrations.AddField(
            model_name='exam',
            name='exam_paper',
            field=models.FileField(
                blank=True,
                help_text='上传考试试卷（PDF/Word/PPT格式）',
                null=True,
                upload_to='exam_papers/%Y/%m/',
                verbose_name='考试试卷',
            ),
        ),
        # 创建 AnswerLog 模型
        migrations.CreateModel(
            name='AnswerLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_answer', models.TextField(blank=True, default='', verbose_name='变更前答案')),
                ('new_answer', models.TextField(blank=True, default='', verbose_name='变更后答案')),
                ('action_type', models.CharField(
                    choices=[('answer', '作答'), ('change', '修改'), ('delete', '清除')],
                    default='change',
                    max_length=20,
                    verbose_name='操作类型',
                )),
                ('elapsed_seconds', models.PositiveIntegerField(default=0, help_text='从考试开始到本次作答的累计秒数', verbose_name='答题用时（秒）')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_logs', to='exams.examattempt', verbose_name='考试记录')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_logs', to='exams.question', verbose_name='题目')),
            ],
            options={
                'verbose_name': '答题留痕',
                'verbose_name_plural': '答题留痕',
                'ordering': ['attempt', 'question', 'created_at'],
            },
        ),
    ]
