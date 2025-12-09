from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginOTPViewSet, OTPLoginViewSet, UserView, CookieTokenRefreshView, LogoutView

router = DefaultRouter()
app_name = "auth_api"

router.register(r'login_otp', LoginOTPViewSet, basename="login_otp")
router.register(r'verify_login_otp', OTPLoginViewSet, basename="verify_login_otp")

urlpatterns = [
    path('', include(router.urls)),
    path('user/', UserView.as_view(), name="user"),
    path('refresh/', CookieTokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', LogoutView.as_view(), name="logout"),
]
