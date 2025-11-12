from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EnquiryViewSet

app_name = "contact_api"

router = DefaultRouter()

router.register(r'', EnquiryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
