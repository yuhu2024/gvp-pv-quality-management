# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter
def dict_get(dictionary, key):
    """从字典中获取指定key的值"""
    if dictionary is None:
        return None
    return dictionary.get(key)
