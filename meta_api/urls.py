from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MetaTagViewSet

app_name = "meta_api"

router = DefaultRouter()

router.register(r'', MetaTagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

