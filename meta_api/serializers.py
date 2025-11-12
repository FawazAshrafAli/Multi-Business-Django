from rest_framework import serializers

from base.models import MetaTag

class MetaTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaTag
        fields = [
            "name", "description", "meta_title", "meta_description", "slug", "updated"
            ]
        
class MiniMetaTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaTag
        fields = [
            "name", "slug"
            ]