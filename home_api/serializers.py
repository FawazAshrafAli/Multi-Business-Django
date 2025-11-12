from rest_framework import serializers
from home.models import HomeContent


class HomeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeContent
        fields = ["title", "description", "footer_text", "meta_title", "meta_description", "updated"]