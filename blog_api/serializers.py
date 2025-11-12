from rest_framework import serializers
from django.conf import settings
from django.db.models import Q

from blog.models import Blog
from meta_api.serializers import MetaTagSerializer

class BlogSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    published_on = serializers.CharField(source="get_published_on", read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    meta_tags = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ["id",
            "title", "image_url", "published_date", "updated", 
            "get_absolute_url", "summary", "meta_tags", "slug", 
            "published_on", "content",
            "meta_description", "company_slug"
            ]
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}/{obj.image.url}"
        
        return None
    
    def get_meta_tags(self, obj):
        if obj.meta_tags:
            meta_tags = obj.meta_tags.order_by("?")[:12]

            serializers = MetaTagSerializer(meta_tags, many=True)
            return serializers.data
        
        return None    