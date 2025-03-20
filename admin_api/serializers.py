from rest_framework import serializers
from .models import otpwhatsapp

class OTPWhatsAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = otpwhatsapp
        fields = ['id', 'phone_number', 'otp', 'created_at']
        read_only_fields = ['created_at'] 