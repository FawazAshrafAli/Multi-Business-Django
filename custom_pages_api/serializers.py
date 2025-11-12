from rest_framework import serializers

from custom_pages.models import (
    FAQ, AboutUs, ContactUs, PrivacyPolicy, TermsAndCondition, 
    ShippingAndDeliveryPolicy, CancellationAndRefundPolicy
    )

class FaqSerializer(serializers.ModelSerializer):
    company_slug = serializers.CharField(source="company.slug", read_only = True)

    class Meta:
        model = FAQ
        fields = [
            "question", "short_answer", "answer", "slug", "updated", "created", "company_slug"
        ]


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = [
            "content", "effective_date", 
            "slug", "created", "updated"
        ]


class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndCondition
        fields = [
            "content", "effective_date", "slug"
        ]


class ShippingAndDeliveryPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAndDeliveryPolicy
        fields = [
            "content", "slug"
        ]


class CancellationAndRefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationAndRefundPolicy
        fields = [
            "content", "slug"
        ]


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = [
            "content", "slug", "created", "updated"
        ]
        

class ContactUsSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source="place.name", read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = ContactUs
        fields = [
            "email", "tel", "mobile", "provide_query", "place_name", "district_name",
            "state_name", "pincode", "web", "address", 
            "lat", "lon", "slug", "address"
        ]