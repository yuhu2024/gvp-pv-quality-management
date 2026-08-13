"""
电子签名 - URL配置
"""
from django.urls import path
from . import views

app_name = 'signatures'

urlpatterns = [
    path('pad/', views.signature_pad_view, name='pad'),
    path('api/save/', views.save_signature_api, name='save_api'),
    path('<int:pk>/', views.signature_detail_view, name='detail'),
    path('qrcode/<int:course_id>/', views.checkin_qrcode_view, name='checkin_qrcode'),
    path('qrcode/<int:course_id>/image/', views.checkin_qrcode_image_view, name='qrcode_image'),
    path('mobile/checkin/<int:course_id>/', views.mobile_checkin_view, name='mobile_checkin'),
]
