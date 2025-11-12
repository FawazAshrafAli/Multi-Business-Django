from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    SubTypeViewset, CompanyViewSet, DetailViewSet, TypeViewSet, 
    EnquiryViewSet, RegistrationViewset, DetailSliderViewSet, 
    DetailListViewSet
    )

app_name = "registration_api"

router = DefaultRouter()

router.register(r'companies', CompanyViewSet, basename="company")

companies_router = NestedDefaultRouter(router, r'companies', lookup = "company")

companies_router.register(r'details', DetailViewSet, basename="company-detail")
companies_router.register(r'detail-list', DetailListViewSet, basename="company-detail-list")
companies_router.register(r'slider-details', DetailSliderViewSet, basename="company-slider-detail")
companies_router.register(r'types', TypeViewSet, basename="company-type")
companies_router.register(r'sub_types', SubTypeViewset, basename="company-sub_type")
companies_router.register(r'registrations', RegistrationViewset, basename="company-registration")
companies_router.register(r'enquiries', EnquiryViewSet, basename="company-enquiry")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(companies_router.urls)),
]
