from rest_framework import viewsets
from django.db.models import F, FloatField, ExpressionWrapper, Value
from django.db.models.functions import Sqrt

from .serializers import DestinationSerializer
from directory.models import Destination

class DestinationApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = DestinationSerializer

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return Destination.objects.none()

        distance_expr = Sqrt(
            (F('latitude') - Value(lat)) ** 2 +
            (F('longitude') - Value(lon)) ** 2
        )

        return Destination.objects.annotate(
            distance=ExpressionWrapper(distance_expr, output_field=FloatField())
        ).filter(latitude__isnull=False, longitude__isnull=False).order_by('distance')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class SliderDestinationApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = DestinationSerializer

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return Destination.objects.none()

        distance_expr = Sqrt(
            (F('latitude') - Value(lat)) ** 2 +
            (F('longitude') - Value(lon)) ** 2
        )

        return Destination.objects.annotate(
            distance=ExpressionWrapper(distance_expr, output_field=FloatField())
        ).filter(latitude__isnull=False, longitude__isnull=False).order_by('distance')[:12]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    