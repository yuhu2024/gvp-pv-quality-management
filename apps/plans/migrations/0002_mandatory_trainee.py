from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('plans', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingplan',
            name='deadline',
            field=models.DateField(blank=True, help_text='所有参训人员必须在此日期前完成培训和考试', null=True, verbose_name='培训截止日期'),
        ),
        migrations.AddField(
            model_name='trainingplan',
            name='is_mandatory',
            field=models.BooleanField(default=False, help_text='开启后，指定人员必须在时限内完成培训和考试', verbose_name='是否强制培训'),
        ),
        migrations.AddField(
            model_name='trainingplan',
            name='require_exam_pass',
            field=models.BooleanField(default=True, help_text='开启后，考试不通过者需继续学习并重考，直到通过', verbose_name='要求考试必须通过'),
        ),
        migrations.AddField(
            model_name='trainingplan',
            name='allow_retake',
            field=models.BooleanField(default=True, help_text='考核不通过时是否允许重新考试', verbose_name='允许重复考试'),
        ),
        migrations.AddField(
            model_name='trainingplan',
            name='max_attempts',
            field=models.PositiveIntegerField(default=0, help_text='0=不限次数，考试不通过需重考直到通过或达到上限', verbose_name='最大考试次数'),
        ),
        migrations.CreateModel(
            name='MandatoryTrainee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', '未开始'), ('learning', '学习中'), ('exam_pending', '待考试'), ('passed', '已通过'), ('failed', '未通过（需重考）'), ('overdue', '已逾期')], default='pending', max_length=20, verbose_name='状态')),
                ('assigned_at', models.DateTimeField(auto_now_add=True, verbose_name='分配时间')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='完成时间')),
                ('exam_attempts', models.PositiveIntegerField(default=0, verbose_name='考试次数')),
                ('last_exam_score', models.PositiveIntegerField(blank=True, null=True, verbose_name='最近考试得分')),
                ('remark', models.TextField(blank=True, default='', verbose_name='备注')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mandatory_trainees', to='plans.trainingplan', verbose_name='所属培训计划')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mandatory_trainings', to=settings.AUTH_USER_MODEL, verbose_name='参训人员')),
            ],
            options={
                'verbose_name': '强制培训人员',
                'verbose_name_plural': '强制培训人员名单',
                'ordering': ['assigned_at'],
                'unique_together': {('plan', 'user')},
            },
        ),
    ]
