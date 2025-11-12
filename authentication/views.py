from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, View, RedirectView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import logging
from random import randint

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError

from superadmin.views import AdminBaseView
from .models import EmailVerificationOtp

logger = logging.getLogger(__name__)

class LoginView(TemplateView):
    template_name = 'superadmin/login.html'
    success_url = reverse_lazy("superadmin:home")
    redirect_url = reverse_lazy("authentication:login")    

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    return redirect(self.success_url)
                else:
                    return redirect(reverse_lazy("company:home"))
        
            return render(request, self.template_name)
        except Exception as e:
            logger.exception(f"Error in get method of login view: {e}")

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        url = self.redirect_url
        error_message = None

        try:
            username = request.POST.get("username")
            password = request.POST.get("password")

            if not username or not password:
                error_message = "Please provide both username and password."
            else:  
                user = authenticate(request, username = username.strip(), password = password)

                if user is not None:
                    login(request, user)
                    if user.is_superuser:
                        url = self.success_url
                    else:
                        url = reverse_lazy('customer:home')
                else:
                    error_message = "Failed! Invalid credentials."
                
        except Exception as e:
            error_message = "Login Failed."
            logger.error(f"Error in post method of login view: {e}")
        
        if error_message:
            messages.error(request, error_message)
        return redirect(url)
    

class CustomerLoginView(TemplateView):
    template_name = 'customer/login.html'
    success_url = reverse_lazy("customer:home")
    redirect_url = reverse_lazy("authentication:customer_login")    

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                if not request.user.is_superuser:
                    return redirect(self.success_url)
                else:
                    return redirect(reverse_lazy("superadmin:home"))
        
            return render(request, self.template_name)
        except Exception as e:
            logger.exception(f"Error in get method of login view: {e}")

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        url = self.redirect_url
        error_message = None

        try:
            username = request.POST.get("username")
            password = request.POST.get("password")            

            if not username or not password:
                error_message = "Please provide both username and password."
            else:  
                user = authenticate(request, username = username.strip(), password = password)

                if user is not None and not user.is_superuser:
                    login(request, user)
                    url = self.success_url
                else:
                    error_message = "Failed! Invalid credentials."
                
        except Exception as e:
            error_message = "Login Failed."
            logger.error(f"Error in post method of login view: {e}")
        
        if error_message:
            messages.error(request, error_message)
        return redirect(url)
    

class LogoutView(RedirectView):
    redirect_url = reverse_lazy("authentication:login")

    def get(self, request, *args, **kwargs):
        try:
            logout(request)

        except Exception as e:
            logger.error(f"Error occured during logout: {e}")
            messages.error(request, "Logout Failed.")
        
        return redirect(self.redirect_url)


class SendEmailVerificationOtpView(AdminBaseView, View):
    model = EmailVerificationOtp

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            otp = randint(100000, 999999)
            new_email = request.POST.get("new_email")

            if not user or not otp or not new_email:
                return JsonResponse({"status": "failed", "error_msg": "Bad Request"}, status=400)
            
            self.model.objects.update_or_create(user = user, defaults={"otp": otp, "email": new_email})

            subject = "Your OTP Code For Email Verification"
            message = f"Your OTP code for email verification is {otp}. It is valid for the next 10 minutes."
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [new_email]

            send_mail(subject, message, email_from, recipient_list)

            return JsonResponse({"status": "success"}, status=201)

        except Exception as e:
            logger.exception(f"Error in SendVerificationEmailOtpView of authentication app: {e}")
            return JsonResponse({"status": "failed", "error_msg": "An unexpected error occured"}, status=500)

        
class VerifyEmailView(AdminBaseView, View):
    model = EmailVerificationOtp

    def get(self, request, *args, **kwargs):
        try:
            otp = request.GET.get("otp")
            user = request.user
            username = user.username

            if not otp or not user:
                return JsonResponse({"status": "failed", "error_msg": "Bad Request"}, status=400)
            
            otp_obj = self.model.objects.filter(user = user, otp = otp).first()

            if not otp_obj:
                return JsonResponse({"status": "failed", "user_msg": "Invalid OTP"}, status=400)
            
            if timezone.now() > otp_obj.updated + timedelta(minutes=10):
                return JsonResponse({"status": "failed", "user_msg": "OTP has expired. Please request a new OTP"}, status=408)
            
            return JsonResponse({"status": "success"}, status=200)

        except Exception as e:
            logger.exception(f"Error in VerifyEmailView of authentication app: {e}")
            return JsonResponse({"status": "failed", "error_msg": "An unexpected error occured"}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    if request.user.is_authenticated:
        return Response({
            "username": request.user.username,
            "email": request.user.email
        }, status=200)
    return Response({"detail": "Not authenticated"}, status=401)


@api_view(["POST"])
def user_login(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return Response(
            {"success": False, "message": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=email.strip(), password=password)
    if not user:
        return Response(
            {"success": False, "message": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    login(request, user)
    return Response({"success": True}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"success": "Logged out successfully"}, status=205)
    except TokenError as e:
        # If token is already blacklisted or invalid
        return Response({"error": "Token is invalid or already blacklisted"}, status=400)
    except Exception as e:
        print(f"Logout error: {e}")
        return Response({"error": "Logout failed"}, status=400)