"""
大模型统一客户端 - 兼容 OpenAI 接口格式

支持：
  - Kimi (Moonshot AI)     base_url: https://api.moonshot.cn/v1
  - 豆包 (火山引擎/Ark)    base_url: https://ark.cn-beijing.volces.com/api/v3
  - 阿里千问 (DashScope)    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
  - OpenAI                 base_url: https://api.openai.com/v1
  - 任意 OpenAI 兼容接口
"""
import json
import time
import urllib.request
import urllib.error

from .models import LLMProvider, AIUsageLog


class LLMError(Exception):
    """LLM 调用异常"""
    pass


class LLMClient:
    """统一大模型客户端"""

    def __init__(self, provider=None):
        """
        初始化客户端
        :param provider: LLMProvider 实例，为 None 时使用默认配置
        """
        if provider is None:
            provider = LLMProvider.get_default()
        if provider is None:
            raise LLMError('未配置大模型，请先在管理后台添加模型配置并设为默认。')

        self.provider = provider
        self.base_url = provider.base_url.rstrip('/')
        self.api_key = provider.api_key
        self.model = provider.model_name
        self.temperature = provider.temperature
        self.max_tokens = provider.max_tokens

    def chat(self, messages, temperature=None, max_tokens=None, task_type='other', user=None, input_text=''):
        """
        调用 chat completions 接口

        :param messages: 消息列表 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        :param temperature: 温度参数，覆盖默认值
        :param max_tokens: 最大token数，覆盖默认值
        :param task_type: 任务类型（用于日志记录）
        :param user: 调用用户
        :param input_text: 原始输入文本（用于日志）
        :return: AI 回复的文本内容
        """
        url = f'{self.base_url}/chat/completions'
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature if temperature is not None else self.temperature,
            'max_tokens': max_tokens if max_tokens is not None else self.max_tokens,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        start_time = time.time()
        error_msg = ''

        try:
            req_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
            # 30秒超时
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode('utf-8'))

            duration_ms = int((time.time() - start_time) * 1000)
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            usage = result.get('usage', {})

            # 记录日志
            AIUsageLog.objects.create(
                provider=self.provider,
                task_type=task_type,
                input_text=input_text[:5000],
                output_text=content[:5000],
                prompt_tokens=usage.get('prompt_tokens', 0),
                completion_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                duration_ms=duration_ms,
                is_success=True,
                created_by=user,
            )

            return content

        except urllib.error.HTTPError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_body = ''
            try:
                error_body = e.read().decode('utf-8')
            except Exception:
                pass
            error_msg = f'HTTP {e.code}: {error_body[:500]}'

        except urllib.error.URLError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f'连接错误: {str(e)}'

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = f'未知错误: {str(e)}'

        # 记录失败日志
        AIUsageLog.objects.create(
            provider=self.provider,
            task_type=task_type,
            input_text=input_text[:5000],
            is_success=False,
            error_message=error_msg,
            duration_ms=duration_ms,
            created_by=user,
        )

        raise LLMError(error_msg)

    def chat_with_system(self, system_prompt, user_prompt, **kwargs):
        """便捷方法：带系统提示的对话"""
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]
        return self.chat(messages, input_text=user_prompt, **kwargs)