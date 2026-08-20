# -*- coding: utf-8 -*-
"""config 应用的自定义模板标签和过滤器"""
import json
from django import template

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """从字典中获取指定key的值（支持模板中使用 dict|lookup:'key' 语法）"""
    if dictionary is None:
        return None
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def safe_json(value):
    """将 Python 对象转为 JSON 字符串，便于在 JS 中使用"""
    try:
        return json.dumps(value, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return '{}'
