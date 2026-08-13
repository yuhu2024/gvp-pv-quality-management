# Generated manually on 2026-07-24

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
            name='LLMProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='如：Kimi生产环境', max_length=100, verbose_name='配置名称')),
                ('provider', models.CharField(choices=[('kimi', 'Kimi (Moonshot AI)'), ('doubao', '豆包 (火山引擎)'), ('qwen', '阿里千问 (DashScope)'), ('openai', 'OpenAI'), ('custom', '自定义 (OpenAI兼容)')], default='kimi', max_length=20, verbose_name='服务商')),
                ('api_key', models.CharField(help_text='各平台的API密钥', max_length=500, verbose_name='API Key')),
                ('base_url', models.URLField(help_text='OpenAI兼容的API地址，如：https://api.moonshot.cn/v1', max_length=500, verbose_name='API地址')),
                ('model_name', models.CharField(help_text='如：moonshot-v1-8k, doubao-pro-32k, qwen-plus', max_length=200, verbose_name='模型名称')),
                ('temperature', models.FloatField(default=0.7, help_text='0-2之间，值越低输出越确定，值越高越有创造力', verbose_name='温度参数')),
                ('max_tokens', models.PositiveIntegerField(default=4096, verbose_name='最大Token数')),
                ('is_active', models.BooleanField(default=True, verbose_name='启用')),
                ('is_default', models.BooleanField(default=False, help_text='设为默认后，AI功能将使用此配置', verbose_name='默认模型')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '大模型配置',
                'verbose_name_plural': '大模型配置',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIUsageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.CharField(choices=[('generate_questions', 'AI出题'), ('grade_essay', 'AI批改'), ('summarize', '生成摘要'), ('ppt_outline', 'PPT大纲'), ('chat', '对话'), ('other', '其他')], default='other', max_length=30, verbose_name='任务类型')),
                ('input_text', models.TextField(blank=True, default='', verbose_name='输入内容')),
                ('output_text', models.TextField(blank=True, default='', verbose_name='输出内容')),
                ('prompt_tokens', models.PositiveIntegerField(default=0, verbose_name='输入Token')),
                ('completion_tokens', models.PositiveIntegerField(default=0, verbose_name='输出Token')),
                ('total_tokens', models.PositiveIntegerField(default=0, verbose_name='总Token')),
                ('duration_ms', models.PositiveIntegerField(default=0, verbose_name='耗时（毫秒）')),
                ('is_success', models.BooleanField(default=True, verbose_name='是否成功')),
                ('error_message', models.TextField(blank=True, default='', verbose_name='错误信息')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='调用时间')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_usage_logs', to=settings.AUTH_USER_MODEL, verbose_name='调用者')),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usage_logs', to='llm.llmprovider', verbose_name='使用的模型')),
            ],
            options={
                'verbose_name': 'AI调用日志',
                'verbose_name_plural': 'AI调用日志',
                'ordering': ['-created_at'],
            },
        ),
    ]