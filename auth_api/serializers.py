from rest_framework import serializers
from authentication.models import LoginOtp

class LoginOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginOtp
        fields = ["id", "email", "otp", "created", "updated"]