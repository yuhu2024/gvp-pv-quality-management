"""
URL configuration for training_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('courses/', include('apps.courses.urls')),
    path('exams/', include('apps.exams.urls')),
    path('plans/', include('apps.plans.urls')),
    # my-tasks 通过 plans:my_tasks 访问 -> /plans/my-tasks/
    path('logs/', include('apps.logs.urls')),
    path('settings/', include('apps.config.urls')),
    path('certificates/', include('apps.certificates.urls')),
    path('ranking/', include('apps.ranking.urls')),
    path('signature/', include('apps.signatures.urls')),
    path('question-bank/', include('apps.question_bank.urls')),
    path('llm/', include('apps.llm.urls')),
    path('matrix/', include('apps.training_matrix.urls')),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
