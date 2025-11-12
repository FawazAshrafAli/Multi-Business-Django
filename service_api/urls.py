from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from django.urls import path, include
from .views import (
    ServiceViewset, CompanyViewSet, DetailViewSet, EnquiryViewSet,
    SubCategoryViewset, CategoryViewset, ServiceSliderDetailViewSet, 
    DetailListViewSet 
    )

app_name = "service_api"

router = DefaultRouter()

router.register(r'companies', CompanyViewSet, basename="company")

companies_router = NestedDefaultRouter(router, r'companies', lookup = "company")

companies_router.register(r'services', ServiceViewset, basename="company-service")
companies_router.register(r'details', DetailViewSet, basename="company-detail")
companies_router.register(r'detail-list', DetailListViewSet, basename="company-detail-list")
companies_router.register(r'slider-details', ServiceSliderDetailViewSet, basename="company-slider-detail")
companies_router.register(r'enquiries', EnquiryViewSet, basename="company-enquiry")
companies_router.register(r'sub_categories', SubCategoryViewset, basename="company-sub_category")
companies_router.register(r'categories', CategoryViewset, basename="company-category")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(companies_router.urls)),
]
