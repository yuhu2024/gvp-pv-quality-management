"""
用户与账号管理 - 表单
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User, Department, Role


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名',
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码',
        })
    )


class UserProfileForm(forms.ModelForm):
    """用户个人资料表单（用户编辑自己的资料）"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'gender', 'department', 'position', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class UserForm(forms.ModelForm):
    """创建/编辑用户表单（管理员用）"""
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='留空则不修改密码',
    )
    password_confirm = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'first_name', 'last_name',
                  'employee_id', 'department', 'role', 'position', 'gender',
                  'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 编辑模式下密码非必填
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['password_confirm'].required = False
        else:
            # 创建模式下密码必填
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError('两次输入的密码不一致')
        return password_confirm

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        # 编辑模式下排除自身
        qs = User.objects.filter(employee_id=employee_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('该工号已存在')
        return employee_id

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class ExcelImportForm(forms.Form):
    """Excel文件上传表单（批量导入用户）"""
    excel_file = forms.FileField(
        label='选择Excel文件',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
        }),
        help_text='支持 .xlsx 和 .xls 格式'
    )

    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ('xlsx', 'xls'):
                raise ValidationError('仅支持 .xlsx 或 .xls 格式的文件')
            if file.size > 10 * 1024 * 1024:  # 10MB限制
                raise ValidationError('文件大小不能超过10MB')
        return file
