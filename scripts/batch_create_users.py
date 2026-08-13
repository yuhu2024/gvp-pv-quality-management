#!/usr/bin/env python
"""
Django管理命令 - 批量创建用户
用法:
    python manage.py batch_create_users
    python manage.py batch_create_users --count 500
    python manage.py batch_create_users --prefix employee --department 技术部 --role 管理员
"""

import os
import sys
import argparse

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'training_system.settings')

import django
django.setup()

from apps.users.models import User, Department, Role


def batch_create_users(count=300, prefix='trainee', department=None, role=None):
    """
    批量创建用户

    Args:
        count: 创建数量
        prefix: 用户名前缀
        department: 部门名称
        role: 角色名称

    Returns:
        tuple: (成功数, 失败数, 失败详情列表)
    """
    success_count = 0
    fail_count = 0
    fail_details = []

    # 默认密码
    default_password = 'Abc@12345'

    # 获取或创建部门
    dept_obj = None
    if department:
        dept_obj, _ = Department.objects.get_or_create(name=department)

    # 获取或创建角色
    role_obj = None
    if role:
        role_obj, _ = Role.objects.get_or_create(
            code=role,
            defaults={'name': role}
        )

    print(f'===== 批量创建用户 =====')
    print(f'数量: {count}')
    print(f'前缀: {prefix}')
    print(f'部门: {department or "无"}')
    print(f'角色: {role or "无"}')
    print(f'默认密码: {default_password}')
    print(f'开始创建...\n')

    for i in range(1, count + 1):
        # 自动生成用户名（如 trainee001, trainee002...）
        username = f'{prefix}{i:03d}'
        employee_id = f'{prefix.upper()}{i:04d}'

        try:
            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                fail_count += 1
                detail = f'{username}: 用户名已存在'
                fail_details.append(detail)
                print(f'[跳过] {detail}')
                continue

            # 创建用户
            user = User.objects.create_user(
                username=username,
                password=default_password,
                employee_id=employee_id,
                department=dept_obj,
            )

            # 分配角色
            if role_obj:
                user.roles.add(role_obj)

            success_count += 1
            if success_count % 50 == 0:
                print(f'  ... 已创建 {success_count} 个用户')

        except Exception as e:
            fail_count += 1
            detail = f'{username}: {str(e)}'
            fail_details.append(detail)
            print(f'[失败] {detail}')

    print(f'\n===== 批量创建完成 =====')
    print(f'成功: {success_count} 个')
    print(f'失败: {fail_count} 个')
    if fail_details:
        print(f'\n失败详情（前20条）:')
        for detail in fail_details[:20]:
            print(f'  - {detail}')
        if len(fail_details) > 20:
            print(f'  ... 还有 {len(fail_details) - 20} 条失败记录')

    return success_count, fail_count, fail_details


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量创建用户')
    parser.add_argument('--count', type=int, default=300, help='创建数量（默认300）')
    parser.add_argument('--prefix', type=str, default='trainee', help='用户名前缀（默认 trainee）')
    parser.add_argument('--department', type=str, default=None, help='部门名称')
    parser.add_argument('--role', type=str, default='学员', help='角色名称（默认 "学员"）')

    args = parser.parse_args()

    batch_create_users(
        count=args.count,
        prefix=args.prefix,
        department=args.department,
        role=args.role,
    )
