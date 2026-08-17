"""生成 SystemTimeOffset 模型迁移"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemTimeOffset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offset_seconds', models.BigIntegerField(default=0, help_text='正数=时间快进，负数=时间回退。如 86400=快进1天，-3600=回退1小时', verbose_name='时间偏移（秒）')),
                ('is_active', models.BooleanField(default=False, help_text='关闭后系统使用真实时间', verbose_name='是否启用')),
                ('access_key', models.CharField(default='JHM-PV-2026-TIME', help_text='隐藏页面的访问密钥，修改后需使用新密钥访问', max_length=128, verbose_name='访问密钥')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('last_modified_by', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user', verbose_name='最后修改人')),
            ],
            options={
                'verbose_name': '系统时间偏移',
                'verbose_name_plural': '系统时间偏移',
            },
        ),
    ]
