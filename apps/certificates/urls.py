from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.certificate_list_view, name='list'),
    path('<int:pk>/', views.certificate_detail_view, name='detail'),
    path('<int:pk>/download/', views.certificate_download_view, name='download'),
    path('templates/', views.template_list_view, name='template_list'),
    path('templates/create/', views.template_create_view, name='template_create'),
    path('templates/<int:pk>/edit/', views.template_edit_view, name='template_edit'),
    path('issue/', views.issue_certificate_view, name='issue'),
]