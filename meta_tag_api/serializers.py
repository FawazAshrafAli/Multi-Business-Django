from rest_framework import serializers

from base.models import MetaTag

class MetaTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = MetaTag
        fields = ["name", "slug", "description", "meta_description", "updated"]
    

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
    meta_tags = MetaTagSerializer(many=True)

    mode = serializers.CharField(allow_blank=True, required=False)
    start_date = serializers.CharField(allow_blank=True, required=False)
    end_date = serializers.CharField(allow_blank=True, required=False)
    duration = serializers.CharField(allow_blank=True, required=False)
    category = serializers.CharField(allow_blank=True, required=False)
    rating = serializers.CharField(allow_blank=True, required=False)
    rating_count = serializers.CharField(allow_blank=True, required=False)

    url = serializers.CharField(allow_blank=True, required=False)
    updated  = serializers.CharField(allow_blank=True, required=False)
    url_type = serializers.CharField(allow_blank=True, required=False)
