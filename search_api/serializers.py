from rest_framework import serializers

class ItemSerializer(serializers.Serializer):
    title = serializers.CharField()
    summary = serializers.CharField()
    company_name = serializers.CharField()
    company_type_name = serializers.CharField()
    company_type_slug = serializers.CharField()
    company_slug = serializers.CharField()
    slug = serializers.CharField()
    image_url = serializers.CharField(allow_blank=True, required=False)
    meta_description = serializers.CharField()
    price = serializers.CharField()

    mode = serializers.CharField(allow_blank=True, required=False)
    start_date = serializers.CharField(allow_blank=True, required=False)
    end_date = serializers.CharField(allow_blank=True, required=False)
    duration = serializers.CharField(allow_blank=True, required=False)
    category = serializers.CharField(allow_blank=True, required=False)
    rating = serializers.CharField(allow_blank=True, required=False)
    rating_count = serializers.CharField(allow_blank=True, required=False)
    url = serializers.CharField()