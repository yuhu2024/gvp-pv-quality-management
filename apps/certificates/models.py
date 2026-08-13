"""
荣誉证书 - 数据模型
"""
import uuid

from django.db import models
from django.conf import settings


def generate_cert_no():
    """生成唯一证书编号"""
    return uuid.uuid4().hex[:16].upper()


class CertificateTemplate(models.Model):
    """证书模板"""
    name = models.CharField('模板名称', max_length=200)
    description = models.TextField('模板描述', blank=True, default='')
    background_image = models.ImageField(
        '背景图片', upload_to='certificates/templates/', null=True, blank=True
    )
    content_template = models.TextField('内容模板', default='''培训合格证书

{username} 同学：

您已完成《{course_title}》培训课程的学习，
综合成绩：{score} 分，
特发此证，以资鼓励。

颁发日期：{date}
证书编号：{cert_no}
''')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '证书模板'
        verbose_name_plural = '证书模板'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def render(self, user, course, score, cert_no):
        """渲染证书内容（自动转义防 XSS）"""
        from django.utils import timezone
        from django.utils.html import escape
        return self.content_template.format(
            username=escape(user.get_full_name() or user.username),
            course_title=escape(course.title),
            score=escape(str(score)),
            date=timezone.now().strftime('%Y年%m月%d日'),
            cert_no=escape(str(cert_no)),
        )


class Certificate(models.Model):
    """证书"""
    template = models.ForeignKey(
        CertificateTemplate, on_delete=models.PROTECT,
        related_name='certificates', verbose_name='证书模板'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='certificates', verbose_name='用户'
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE,
        related_name='certificates', verbose_name='课程'
    )
    cert_no = models.CharField('证书编号', max_length=50, unique=True, default=generate_cert_no)
    score = models.DecimalField('成绩', max_digits=5, decimal_places=2)
    issued_at = models.DateTimeField('颁发时间', auto_now_add=True)
    is_revoked = models.BooleanField('是否已撤销', default=False)
    revoked_at = models.DateTimeField('撤销时间', null=True, blank=True)
    revoke_reason = models.CharField('撤销原因', max_length=500, blank=True, default='')

    class Meta:
        verbose_name = '证书'
        verbose_name_plural = '证书'
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.cert_no} - {self.user} - {self.course.title}'