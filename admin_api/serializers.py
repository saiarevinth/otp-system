from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import otpwhatsapp

class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'"
            )
        ]
    )

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'"
            )
        ]
    )
    otp = serializers.CharField(max_length=6)

class OTPWhatsAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = otpwhatsapp
        fields = ['id', 'phone_number', 'created_at']
        read_only_fields = ['created_at'] 