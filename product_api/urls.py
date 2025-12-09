from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from django.urls import path, include
from .views import (
    ProductDetailViewset, ProductCompanyViewSet, 
    ProductCategoryViewSet, ProductViewset, EnquiryViewSet,
    ProductSubCategoryViewSet, ReviewViewSet, 
    ProductMultipageViewSet, ProductSliderDetailViewset, 
    DetailListViewset, MinProductCategoryViewSet, 
    HomeProductCategoryViewSet, CartViewSet, AddressViewSet,
    OrderViewSet
    )

app_name = "product_api"

router = DefaultRouter()
cart_router = DefaultRouter()
address_router = DefaultRouter()
order_router = DefaultRouter()

router.register(r'companies', ProductCompanyViewSet, basename="company")
cart_router.register(r'cart', CartViewSet, basename="cart")
address_router.register(r'address', AddressViewSet, basename="address")
order_router.register(r'order', OrderViewSet, basename="order")

companies_router = NestedDefaultRouter(router, r'companies', lookup="company")

companies_router.register(r'products', ProductViewset, basename="company-product")
companies_router.register(r'details', ProductDetailViewset, basename="company-detail")
companies_router.register(r'detail-list', DetailListViewset, basename="company-detail-list")
companies_router.register(r'slider-details', ProductSliderDetailViewset, basename="company-slider-detail")
companies_router.register(r'multipages', ProductMultipageViewSet, basename="company-multipage")
companies_router.register(r'categories', ProductCategoryViewSet, basename="company-category")
companies_router.register(r'home-categories', HomeProductCategoryViewSet, basename="company-home-category")
companies_router.register(r'brief-categories', MinProductCategoryViewSet, basename="company-brief-category")
companies_router.register(r'sub_categories', ProductSubCategoryViewSet, basename="company-sub_category")
companies_router.register(r'enquiries', EnquiryViewSet, basename="company-enquiry")
companies_router.register(r'reviews', ReviewViewSet, basename="company-review")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
    path('', include(address_router.urls)),
    path('', include(order_router.urls)),
    path('', include(companies_router.urls)),

]
