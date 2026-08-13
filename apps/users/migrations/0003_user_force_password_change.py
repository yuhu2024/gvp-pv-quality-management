"""
添加 force_password_change 字段到 User 模型
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_permission_role_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='force_password_change',
            field=models.BooleanField(
                default=False,
                help_text='勾选后用户下次登录需修改密码',
                verbose_name='需要修改密码',
            ),
        ),
    ]
