from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import random
from .models import otpwhatsapp
from .serializers import (
    OTPWhatsAppSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer
)
from .otp import sender_otp

# Create your views here.

@csrf_exempt
def otp_form(request):
    return render(request, 'otp_form.html')

def generate_otp():
    return str(random.randint(100000, 999999))

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data['phone_number']
        otp = generate_otp()
        
        # Delete any existing OTP records for this phone number
        otpwhatsapp.objects.filter(phone_number=phone_number).delete()
        
        # Create new OTP record
        otpwhatsapp.objects.create(
            phone_number=phone_number,
            otp=otp,
            created_at=timezone.now()
        )
        
        # Send WhatsApp message
        try:
            message = f"Your verification code is: {otp}"
            sender_otp(phone_number, message)
            return Response({
                'message': 'OTP sent successfully',
                'phone_number': phone_number
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Failed to send OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data['phone_number']
        user_otp = serializer.validated_data['otp']
        
        try:
            # Get most recent OTP within 5 minutes
            otp_record = otpwhatsapp.objects.filter(
                phone_number=phone_number,
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).latest('created_at')
        except otpwhatsapp.DoesNotExist:
            return Response({
                'error': 'OTP expired or invalid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if otp_record.otp == user_otp:
            # Delete OTP after successful verification
            otp_record.delete()
            return Response({
                'message': 'OTP verified successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid OTP'
        }, status=status.HTTP_400_BAD_REQUEST)

class OTPWhatsAppViewSet(viewsets.ModelViewSet):
    queryset = otpwhatsapp.objects.all()
    serializer_class = OTPWhatsAppSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def get_by_phone(self, request):
        phone_number = request.query_params.get('phone_number')
        if phone_number:
            try:
                instance = get_object_or_404(self.queryset, phone_number=phone_number)
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            except otpwhatsapp.DoesNotExist:
                return Response({
                    'error': 'No OTP record found for this phone number'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'error': 'Phone number is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    @action(detail=False, methods=['post'])
    def send_otp(self, request):
        try:
            phone_number = request.data.get('phone_number')
            if not phone_number:
                return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

            otp = self.generate_otp()
            sender_otp(phone_number, f"Your OTP is: {otp}")
            
            otp_record = otpwhatsapp.objects.create(
                phone_number=phone_number,
                otp=otp
            )
            
            return Response({
                'message': 'OTP sent successfully',
                'phone_number': phone_number
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to send OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        try:
            phone_number = request.data.get('phone_number')
            otp = request.data.get('otp')
            
            if not phone_number or not otp:
                return Response({
                    'error': 'Phone number and OTP are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            otp_record = otpwhatsapp.objects.filter(
                phone_number=phone_number
            ).order_by('-created_at').first()
            
            if not otp_record:
                return Response({
                    'error': 'No OTP found for this phone number'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if otp_record.otp == otp:
                otp_record.delete()
                return Response({
                    'message': 'OTP verified successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': f'Verification failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
