"""
培训矩阵 - 应用配置
"""
from django.apps import AppConfig


class TrainingMatrixConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.training_matrix'
    verbose_name = '培训矩阵'