from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NearbyCscCenterViewSet, CscRegistrationViewSet, CscViewSet

app_name = "directory_api"

router = DefaultRouter()

router.register(r'nearby_csc_centers', NearbyCscCenterViewSet)
router.register(r'cscs', CscViewSet, basename="cscs")

urlpatterns = [
    path('', include(router.urls)),
    path('csc_registrations/', CscRegistrationViewSet.as_view({"get": "get"}))
]
