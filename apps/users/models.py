"""
用户与账号管理 - 数据模型
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    """部门模型"""
    name = models.CharField('部门名称', max_length=100, unique=True)
    code = models.CharField('部门编码', max_length=50, unique=True)
    description = models.TextField('部门描述', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """角色模型"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('training_manager', '培训管理员'),
        ('student', '学员'),
    ]

    name = models.CharField('角色名称', max_length=50, choices=ROLE_CHOICES, unique=True)
    code = models.CharField('角色编码', max_length=50, unique=True)
    description = models.TextField('角色描述', blank=True, default='')
    permissions = models.ManyToManyField(
        'Permission', blank=True, related_name='roles', verbose_name='权限列表'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()

    def has_permission(self, module, action):
        """检查角色是否有指定权限"""
        return self.permissions.filter(module=module, action=action).exists()

    def get_permission_codes(self):
        """返回该角色所有权限编码列表"""
        return list(self.permissions.values_list('code', flat=True))


class Permission(models.Model):
    """自定义权限"""
    MODULE_CHOICES = [
        ('dashboard', '仪表盘'),
        ('user', '用户管理'),
        ('course', '课程管理'),
        ('exam', '考试管理'),
        ('plan', '培训计划'),
        ('log', '学习记录'),
        ('report', '数据报表'),
        ('certificate', '证书管理'),
        ('system', '系统配置'),
        ('audit', '审核管理'),
    ]
    ACTION_CHOICES = [
        ('view', '查看'),
        ('create', '创建'),
        ('edit', '编辑'),
        ('delete', '删除'),
        ('export', '导出'),
        ('audit', '审核'),
        ('publish', '发布'),
    ]

    module = models.CharField('模块', max_length=20, choices=MODULE_CHOICES)
    action = models.CharField('操作', max_length=20, choices=ACTION_CHOICES)
    code = models.CharField('权限编码', max_length=50, unique=True)  # 如 course:create
    name = models.CharField('权限名称', max_length=100)  # 如 创建课程
    description = models.CharField('描述', max_length=200, blank=True, default='')

    class Meta:
        unique_together = [['module', 'action']]
        verbose_name = '权限'
        verbose_name_plural = '权限'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """自定义用户模型"""
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('unknown', '未知'),
    ]

    employee_id = models.CharField('工号', max_length=50, unique=True, blank=True, default='')
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='所属部门'
    )
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='角色'
    )
    phone = models.CharField('手机号', max_length=20, blank=True, default='')
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES, default='unknown')
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    position = models.CharField('职位', max_length=100, blank=True, default='')
    is_active = models.BooleanField('是否激活', default=True)
    force_password_change = models.BooleanField('需要修改密码', default=False, help_text='勾选后用户下次登录需修改密码')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']

    def __str__(self):
        display_name = f'{self.last_name}{self.first_name}' if self.last_name or self.first_name else self.username
        return f'{display_name}({self.username})'

    @property
    def is_admin(self):
        """是否为管理员"""
        return self.role and self.role.code == 'admin'

    @property
    def is_training_manager(self):
        """是否为培训管理员"""
        return self.role and self.role.code == 'training_manager'

    def has_module_permission(self, module, action):
        """检查用户（通过角色）是否有指定权限"""
        if self.is_superuser:
            return True
        if not self.role:
            return False
        return self.role.has_permission(module, action)