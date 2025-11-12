from rest_framework import viewsets

from base.models import MetaTag
from meta_api.serializers import MetaTagSerializer

class MetaTagViewSet(viewsets.ModelViewSet):
    serializer_class = MetaTagSerializer
    queryset = MetaTag.objects.all().order_by("name")