from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeContentViewSet

app_name = "home_api"

router = DefaultRouter()

router.register(r'', HomeContentViewSet, basename="home_content")

urlpatterns = [
    path('', include(router.urls)),
]