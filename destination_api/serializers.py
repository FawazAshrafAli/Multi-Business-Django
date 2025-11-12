from rest_framework import serializers
from django.conf import settings

from directory.models import Destination

class DestinationSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()    

    class Meta:
        model = Destination
        fields = [
            "name", "description", "attraction_type", 
            "image_url", "get_place", "get_absolute_url", 
            "slug", "latitude", "longitude", "updated"
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL.rstrip('/')}{obj.image.url}" 
        return None