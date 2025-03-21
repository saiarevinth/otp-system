from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'otp', views.OTPWhatsAppViewSet, basename='otp')

urlpatterns = [
    path('', include(router.urls)),
    path('send-otp/', views.SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('form/', views.otp_form, name='otp_form'),
] 