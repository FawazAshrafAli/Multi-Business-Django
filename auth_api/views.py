from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from authentication.models import LoginOtp
from django.utils import timezone
from datetime import timedelta
import secrets

from .serializers import LoginOtpSerializer

class LoginOTPViewSet(ModelViewSet):
    serializer_class = LoginOtpSerializer
    queryset = LoginOtp.objects.all()
    lookup_field = 'email'

    def retrieve(self, request, *args, **kwargs):
        email = request.query_params.get("email")

        recent_otp = LoginOtp.objects.filter(email = email).first()

        if recent_otp and recent_otp.updated < timezone.now() - timedelta(seconds=30):
            return Response({"error": "Try again after 30 seconds"}, status=status.HTTP_400_BAD_REQUEST)

        otp = secrets.randbelow(900000) + 100000
        login_otp, created = LoginOtp.objects.update_or_create(email = email, defaults={"otp": otp})

        if not login_otp:
            return Response({"error": "OTP not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(login_otp)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)