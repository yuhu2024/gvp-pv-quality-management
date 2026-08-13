"""
大模型管理 - 数据模型
"""
from django.db import models
from django.conf import settings


class LLMProvider(models.Model):
    """大模型服务商配置"""

    PROVIDER_CHOICES = [
        ('kimi', 'Kimi (Moonshot AI)'),
        ('doubao', '豆包 (火山引擎)'),
        ('qwen', '阿里千问 (DashScope)'),
        ('openai', 'OpenAI'),
        ('custom', '自定义 (OpenAI兼容)'),
    ]

    name = models.CharField('配置名称', max_length=100, help_text='如：Kimi生产环境')
    provider = models.CharField('服务商', max_length=20, choices=PROVIDER_CHOICES, default='kimi')
    api_key = models.CharField('API Key', max_length=500, help_text='各平台的API密钥')
    base_url = models.URLField('API地址', max_length=500,
        help_text='OpenAI兼容的API地址，如：https://api.moonshot.cn/v1')
    model_name = models.CharField('模型名称', max_length=200,
        help_text='如：moonshot-v1-8k, doubao-pro-32k, qwen-plus')
    temperature = models.FloatField('温度参数', default=0.7,
        help_text='0-2之间，值越低输出越确定，值越高越有创造力')
    max_tokens = models.PositiveIntegerField('最大Token数', default=4096)
    is_active = models.BooleanField('启用', default=True)
    is_default = models.BooleanField('默认模型', default=False,
        help_text='设为默认后，AI功能将使用此配置')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '大模型配置'
        verbose_name_plural = '大模型配置'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_provider_display()})'

    def save(self, *args, **kwargs):
        # 只允许一个默认
        if self.is_default:
            LLMProvider.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_default(cls):
        """获取默认配置"""
        return cls.objects.filter(is_active=True, is_default=True).first()

    @classmethod
    def get_provider_presets(cls):
        """获取各服务商预设配置"""
        return {
            'kimi': {
                'base_url': 'https://api.moonshot.cn/v1',
                'model_name': 'moonshot-v1-8k',
                'help': '在 platform.moonshot.cn 获取API Key',
            },
            'doubao': {
                'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
                'model_name': 'doubao-seed-2-1-pro-260415',
                'help': '在火山引擎控制台 console.volcengine.com/ark 获取API Key',
            },
            'qwen': {
                'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'model_name': 'qwen-plus',
                'help': '在百炼平台 dashscope.console.aliyun.com 获取API Key',
            },
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'model_name': 'gpt-4o-mini',
                'help': '在 platform.openai.com 获取API Key',
            },
            'custom': {
                'base_url': '',
                'model_name': '',
                'help': '填写任意 OpenAI 兼容的 API 地址',
            },
        }


class AIUsageLog(models.Model):
    """AI调用日志 - 记录每次API调用"""
    TASK_TYPE_CHOICES = [
        ('generate_questions', 'AI出题'),
        ('grade_essay', 'AI批改'),
        ('summarize', '生成摘要'),
        ('ppt_outline', 'PPT大纲'),
        ('chat', '对话'),
        ('other', '其他'),
    ]

    provider = models.ForeignKey(
        LLMProvider, on_delete=models.SET_NULL, null=True,
        related_name='usage_logs', verbose_name='使用的模型'
    )
    task_type = models.CharField('任务类型', max_length=30, choices=TASK_TYPE_CHOICES, default='other')
    input_text = models.TextField('输入内容', blank=True, default='')
    output_text = models.TextField('输出内容', blank=True, default='')
    prompt_tokens = models.PositiveIntegerField('输入Token', default=0)
    completion_tokens = models.PositiveIntegerField('输出Token', default=0)
    total_tokens = models.PositiveIntegerField('总Token', default=0)
    duration_ms = models.PositiveIntegerField('耗时（毫秒）', default=0)
    is_success = models.BooleanField('是否成功', default=True)
    error_message = models.TextField('错误信息', blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='ai_usage_logs', verbose_name='调用者'
    )
    created_at = models.DateTimeField('调用时间', auto_now_add=True)

    class Meta:
        verbose_name = 'AI调用日志'
        verbose_name_plural = 'AI调用日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_task_type_display()}] {self.created_at.strftime("%Y-%m-%d %H:%M")}'