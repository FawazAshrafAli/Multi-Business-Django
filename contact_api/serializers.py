from rest_framework import serializers
from utility.text import clean_string

from .models import Enquiry, UniqueState

class EnquirySerializer(serializers.ModelSerializer):    

    state = serializers.SlugRelatedField(
        queryset = UniqueState.objects.all(),
        slug_field = 'slug'
    )

    phone = serializers.RegexField(
        regex=r'^[^A-Za-z]*$',
        error_messages={
            'invalid': 'Phone number must not contain alphabetic characters.'
        },
        required=True
    )

    class Meta:
        model = Enquiry
        fields = ["name", "phone", "email", "state", "company_sub_type", "item", "comment"]

    def validate(self, data):
        cleaned_data = {}
        for field in ['name', 'phone', 'email']:
            value = clean_string(data.get(field, ''))
            if not value:
                raise serializers.ValidationError({field: f"{field.capitalize()} is required"})
            cleaned_data[field] = value

        if not data.get("state"):
            raise serializers.ValidationError({"state": "State is required"})

        data.update(cleaned_data)
        return data