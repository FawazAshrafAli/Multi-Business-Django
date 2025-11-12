from rest_framework import viewsets
from django.shortcuts import get_list_or_404

from .serializers import (
    FaqSerializer, ContactUsSerializer, PrivacyPolicySerializer, TermsAndConditionsSerializer,
    ShippingAndDeliveryPolicySerializer, CancellationAndRefundPolicySerializer
    )
from custom_pages.models import (
    FAQ, ContactUs, PrivacyPolicy, TermsAndCondition, ShippingAndDeliveryPolicy, 
    CancellationAndRefundPolicy
    )

class FaqViewSet(viewsets.ModelViewSet):
    serializer_class = FaqSerializer
    queryset = FAQ.objects.all().order_by("?")
    lookup_field = "slug"


class ContactUsViewSet(viewsets.ModelViewSet):
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all().order_by("?")
    lookup_field = "company__slug"


class BzindiaFaqsViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = FaqSerializer
    queryset = FAQ.objects.filter(company__isnull = True)
    

class BzindiaContactsViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.filter(company__isnull = True)


class BzindiaPrivacyPolicyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PrivacyPolicySerializer
    queryset = PrivacyPolicy.objects.filter(company__isnull = True)


class BzindiaTermsAndConditionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TermsAndConditionsSerializer
    queryset = TermsAndCondition.objects.filter(company__isnull = True)


class BzindiaShippingAndDeliveryPolicyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShippingAndDeliveryPolicySerializer
    queryset = ShippingAndDeliveryPolicy.objects.filter(company__isnull = True)


class BzindiaCancellationAndRefundPolicyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CancellationAndRefundPolicySerializer
    queryset = CancellationAndRefundPolicy.objects.filter(company__isnull = True)