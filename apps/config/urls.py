from django.urls import path
from . import views

app_name = 'config'

urlpatterns = [
    path('', views.system_config_view, name='settings'),
    path('score-weight/<int:course_pk>/', views.score_weight_view, name='score_weight'),
    path('time-ops/', views.time_ops_view, name='time_ops'),
    path('time-ops/records/', views.training_record_time_view, name='time_ops_records'),
]