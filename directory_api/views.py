from .serializers import MinimalCscCenterSerializer, CscSerializer
from directory.models import CscCenter
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db.models import F, FloatField, Q
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import ACos, Cos, Radians, Sin
from registration.models import RegistrationSubType
from registration_api.serializers import SubTypeSerializer

from .paginations import CscPagination
from utility.location import get_nearby_locations

class NearbyCscCenterViewSet(ReadOnlyModelViewSet):
    model = CscCenter
    serializer_class = MinimalCscCenterSerializer
    queryset = CscCenter.objects.none()

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        if not lat or not lon:
            return self.queryset        

        try:    
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return self.queryset
        
        locations = get_nearby_locations(lat, lon)

        locations_data = list(locations.values_list("name", "district__name", "state__name"))

        query = Q()
        for name, district_name, state_name in locations_data:
            query |= Q(
                place_name=name,
                district_name=district_name,
                state_name=state_name,
            )
        
        difference = 0.55

        start_lat = lat - difference
        start_lon = lon - difference

        end_lat = lat + difference
        end_lon = lon + difference

        starting_point = [start_lat, start_lon]
        ending_point = [end_lat, end_lon]
        
        centers = CscCenter.objects.filter(
            query |
            Q (decimal_latitude__range=(starting_point[0], ending_point[0]),
            decimal_longitude__range=(starting_point[1], ending_point[1]))
        )

        distance_expr = ExpressionWrapper(
            6371
            * ACos(
                Cos(Radians(lat))
                * Cos(Radians(F("decimal_latitude")))
                * Cos(Radians(F("decimal_longitude")) - Radians(lon))
                + Sin(Radians(lat)) * Sin(Radians(F("decimal_latitude")))
            ),
            output_field=FloatField(),
        )

        centers = centers.annotate(distance=distance_expr).order_by("distance")

        return centers
    

class CscRegistrationViewSet(ReadOnlyModelViewSet):
    queryset = RegistrationSubType.objects.none()
    serializer_class = SubTypeSerializer
    
    def get_queryset(self):
        csc_registration_names = list(CscCenter.objects.filter(
            all_registrations__isnull = False
        ).values_list("all_registrations", flat=True))

        unique_csc_registration_names = list(set(csc_registration_names))

        csc_registrations =  RegistrationSubType.objects.filter(
            name__in = unique_csc_registration_names
            ).select_related("type")

        serializer = SubTypeSerializer(csc_registrations, many=True)

        return serializer.data


class CscViewSet(ReadOnlyModelViewSet):
    model = CscCenter
    queryset = model.objects.all()
    serializer_class = CscSerializer
    lookup_field = 'slug'
    pagination_class = CscPagination