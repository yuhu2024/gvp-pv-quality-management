from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('exams', '0004_add_paper_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='allow_retake',
            field=models.BooleanField(default=True, help_text='关闭后，已通过的考试不能再次参加', verbose_name='允许重复考试'),
        ),
        migrations.AddField(
            model_name='exam',
            name='max_attempts',
            field=models.PositiveIntegerField(default=0, help_text='0=不限次数', verbose_name='最大考试次数'),
        ),
        migrations.AddField(
            model_name='exam',
            name='require_pass',
            field=models.BooleanField(default=False, help_text='开启后，未通过者需重考直到通过（配合培训计划的强制培训使用）', verbose_name='必须通过'),
        ),
    ]
