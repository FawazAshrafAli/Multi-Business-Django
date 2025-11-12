from rest_framework import viewsets
from home.models import HomeContent
from .serializers import HomeContentSerializer

class HomeContentViewSet(viewsets.ModelViewSet):
    queryset = HomeContent.objects.all()
    serializer_class = HomeContentSerializer
