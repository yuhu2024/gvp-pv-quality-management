"""
系统时间工具模块

提供带偏移量的系统时间获取函数。
中间件会在每个请求开始时设置偏移量，所有视图通过 get_system_now() 获取系统时间。
"""
import threading
from datetime import timedelta

from django.utils import timezone as dj_timezone

# 线程局部变量，存储当前请求的时间偏移量（秒）
_local = threading.local()


def set_current_offset(seconds):
    """设置当前线程的时间偏移量（由中间件调用）"""
    _local.time_offset = seconds


def get_current_offset():
    """获取当前线程的时间偏移量"""
    return getattr(_local, 'time_offset', 0)


def clear_current_offset():
    """清除当前线程的时间偏移量"""
    if hasattr(_local, 'time_offset'):
        del _local.time_offset


def get_system_now():
    """获取系统当前时间（含偏移量）

    如果中间件设置了偏移量，返回 偏移后 的时间；
    否则返回真实时间。
    """
    real_now = dj_timezone.now()
    offset = get_current_offset()
    if offset:
        return real_now + timedelta(seconds=offset)
    return real_now


def get_system_today():
    """获取系统当前日期（含偏移量）"""
    return get_system_now().date()
