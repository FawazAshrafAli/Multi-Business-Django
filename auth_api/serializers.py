from rest_framework import serializers
from authentication.models import LoginOtp

from django.contrib.auth.models import User 

class LoginOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginOtp
        fields = ["id", "email", "otp", "created", "updated"]


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]