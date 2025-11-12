from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ItemViewSet

app_name = "search_api"

router = DefaultRouter()

router.register(r'results', ItemViewSet)

urlpatterns = [
    path('', include(router.urls))
]
