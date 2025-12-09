from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import viewsets, status
from authentication.models import LoginOtp
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging
import secrets
import time

from .serializers import LoginOtpSerializer, VerifyOtpSerializer, UserSerializer
from authentication.tasks import send_email

logger = logging.getLogger(__name__)

User = get_user_model()

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)    

class LoginOTPViewSet(viewsets.ModelViewSet):
    serializer_class = LoginOtpSerializer
    queryset = LoginOtp.objects.all()
    lookup_field = 'email'

    def send_otp_mail(self, email, otp):
        try:
            subject = "OTP for BZIndia login"
            message = f"Your one time password for login into BZIndia is {otp}. Ignore it if it is not requested by you."
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            fail_silently = False

            send_email.delay(subject, message, from_email, recipient_list, fail_silently)

            return True
        
        except Exception as e:
            logger.exception(f"Error in send_otp_mail function LoginOTPView: {e}")
            return False

    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")

            if not email:
                return Response({"error": "Email was not provided"}, status=status.HTTP_400_BAD_REQUEST)  

            # recent_otp = LoginOtp.objects.filter(email = email).first()

            # if recent_otp and recent_otp.updated < timezone.now() - timedelta(seconds=30):
            #     return Response({"error": "Try again after 30 seconds"}, status=status.HTTP_400_BAD_REQUEST)

            otp = secrets.randbelow(900000) + 100000
            login_otp, created = LoginOtp.objects.update_or_create(email = email, defaults={"otp": otp})

            print(login_otp.otp)

            # if not login_otp:
            #     return Response({"error": "OTP not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # serializer = self.serializer_class(login_otp)  

            # mail_send = False
            # retries = 2

            # while mail_send == False and retries > 0:
            #     time.sleep(2)            
            #     mail_send = self.send_otp_mail(email, login_otp.otp)
            #     retries -= 1

            # if mail_send == True:
            #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.exception(f"Error in create function LoginOTPView: {e}")

        return Response({"error": "Failed! Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class OTPLoginViewSet(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            otp_record = LoginOtp.objects.get(email = email)
        except LoginOtp.DoesNotExist:
            return Response({"error": "OTP not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        if str(otp_record.otp) != str(otp):            
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.updated < (timezone.now() - timedelta(minutes=5)):
            return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        user, _ = User.objects.get_or_create(email = email, username = email)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token   

        response = Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)

        secure_flag = not settings.DEBUG

        cookie_settings = {
            "httponly": True,
            # "secure": False,                 # Set False only for localhost dev
            "secure": secure_flag,   
            # "samesite": None,
            "samesite": "Lax",
            "path": "/",
            # "domain": "localhost"
        } 

        response.set_cookie("access_token", str(access), **cookie_settings)
        response.set_cookie("refresh_token", str(refresh), **cookie_settings)

        return response        

# class CookieTokenRefreshView(TokenRefreshView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         refresh_token = request.COOKIES.get("refresh_token")

#         if not refresh_token:
#             return Response({"error": "No refresh token"}, status=401)

#         try:
#             refresh = RefreshToken(refresh_token)
#             access = refresh.access_token

#             response = Response({"access": str(access)}, status=200)
#             response.set_cookie(
#                 "access_token", str(access),
#                 httponly=True,
#                 secure=False,   # True in production
#                 samesite="Lax",
#                 path="/"
#             )
#             return response

#         except Exception:
#             return Response({"error": "Invalid refresh token"}, status=401)

@method_decorator(csrf_exempt, name="dispatch")
class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "No refresh token"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            secure_flag = not settings.DEBUG

            response = Response({"access": str(access)}, status=200)
            response.set_cookie(
                "access_token", str(access),
                httponly=True,
                secure=secure_flag,
                samesite="Lax" if settings.DEBUG else None,
                path="/",
            )
            return response

        except Exception:
            return Response({"error": "Invalid refresh token"}, status=401)


class LogoutView(APIView):
    def post(self, request):
        response = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)

        # delete cookies
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response