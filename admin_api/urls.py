from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OTPWhatsAppViewSet, otp_form

router = DefaultRouter()
router.register(r'otp-whatsapp', OTPWhatsAppViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('form/', otp_form, name='otp_form'),
] 