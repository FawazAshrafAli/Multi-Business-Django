from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FaqViewSet, ContactUsViewSet, BzindiaFaqsViewset, 
    BzindiaContactsViewset, BzindiaPrivacyPolicyViewSet,
    BzindiaTermsAndConditionsViewSet,
    BzindiaShippingAndDeliveryPolicyViewSet, 
    BzindiaCancellationAndRefundPolicyViewSet
    )

app_name = "custom_pages_api"

router = DefaultRouter()
router.register(r'faqs', FaqViewSet)
router.register(r'bzindia_faqs', BzindiaFaqsViewset, basename = "bzindia_faqs")
router.register(r'contact_us', ContactUsViewSet, basename="contact_us")
router.register(r'bzindia_contacts', BzindiaContactsViewset, basename="bzindia_contacts")
router.register(r'privacy_policy', BzindiaPrivacyPolicyViewSet, basename="privacy_policy")
router.register(r'terms_and_conditions', BzindiaTermsAndConditionsViewSet, basename="terms_and_conditions")
router.register(r'shipping-and-delivery-policy', BzindiaShippingAndDeliveryPolicyViewSet, basename="shipping-and-delivery-policy")
router.register(r'cancellation-and-refund-policy', BzindiaCancellationAndRefundPolicyViewSet, basename="cancellation-and-refund-policy")


urlpatterns = [
    path('', include(router.urls)),
]
