from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginOTPViewSet

router = DefaultRouter()

router.register(r'', LoginOTPViewSet, basename="login_otp")

app_name = "auth_api"

urlpatterns = [
    path('', include(router.urls))
]
