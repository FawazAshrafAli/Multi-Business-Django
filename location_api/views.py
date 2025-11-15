from rest_framework import status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import  Response
from rest_framework.decorators import action

from django.db.models import F, FloatField, ExpressionWrapper, OuterRef, Subquery
from django.db.models.functions import Sqrt
from django.shortcuts import get_object_or_404

from locations.trie_cache import get_place_trie, get_district_trie, get_state_trie

from .serializers import (
    PlaceSerializer, StateSerializer, DistrictSerializer, SimplePlaceSerializer, 
    PlaceCoordinateSerializer, PlacePincodeSerializer, MiniPlaceSerializer,
    PlaceMiniSerializer, MiniPlaceSerializer, MiniStateSerializer, DistrictMiniSerializer,
    MinimalStateSerializer, MinimalDistrictSerializer, BasePlaceSerializer, MinimalPlaceSerializer
    )
from course_api.serializers import MultiPageSerializer
from registration_api.serializers import MultipageSerializer as RegistrationMultipageSerializer
from product_api.serializers import MultiPageSerializer as ProductMultipageSerializer
from service_api.serializers import MultipageSerializer as ServiceMultipageSerializer

from educational.models import MultiPage
from registration.models import MultiPage as RegistrationMultiPage
from product.models import MultiPage as ProductMultiPage
from service.models import MultiPage as ServiceMultiPage
from locations.models import (
    UniqueState, UniqueDistrict, PlaceCoordinate, UniquePlace, PlacePincode
)

from service_api.paginations import ServiceMultipagePagination
from product_api.paginations import ProductMultipagePagination
from course_api.paginations import CourseMultipagePagination
from registration_api.paginations import RegistrationMultipagePagination

from rest_framework.decorators import action

from utility.location import get_nearby_locations

import logging

logger = logging.getLogger(__name__)

class GetNearbyLocationsViewSet(ReadOnlyModelViewSet):
    serializer_class = BasePlaceSerializer
    queryset = UniquePlace.objects.none()

    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        if lat and lon:
            locations = get_nearby_locations(lat, lon)

            return locations if locations else UniquePlace.objects.none()            
        
        return UniquePlace.objects.none()
    

class GetNearestLocationViewSet(ReadOnlyModelViewSet):
    serializer_class = PlaceSerializer
    queryset = PlaceCoordinate.objects.none()

    def get(self, request, *args, **kwargs):
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')

        if not lat or not lon:
            return Response({"place": "Not provided latitude and longitude"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return Response({"place": "Provided values are not coordinates"}, status=status.HTTP_400_BAD_REQUEST)
            
        nearest_place = PlaceCoordinate.objects.annotate(
            distance=ExpressionWrapper(
                Sqrt((F('latitude') - lat) ** 2 + (F('longitude') - lon) ** 2),
                output_field=FloatField()
                )
            ).order_by('distance').first()
        
        place = nearest_place.place
        
        serializer = self.get_serializer(place)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MinimalStateViewset(ReadOnlyModelViewSet):
    queryset = UniqueState.objects.all().order_by("name")
    serializer_class = MinimalStateSerializer
    lookup_field = "slug"


class StateViewset(ReadOnlyModelViewSet):
    queryset = UniqueState.objects.all().order_by("name")
    serializer_class = MiniStateSerializer
    lookup_field = "slug"

    @action(methods=["GET"], detail=True)
    def get_center(self, request, slug=None):
        state = self.get_object()
        if not state:
            return Response({"center": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        qs = PlaceCoordinate.objects.filter(place__state=state).order_by("id").only("id", "latitude", "longitude")
        count = qs.count()

        if count == 0:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        index_of_center_obj = count // 2
        center_obj = qs[index_of_center_obj]   # directly index, no second query

        serializer = PlaceCoordinateSerializer(center_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=True)
    def get_pincode(self, request, slug=None):
        state = self.get_object()

        if not state:
            return Response({"pincode": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        qs = PlaceCoordinate.objects.filter(place__state=state).order_by("id")

        count = qs.count()
        if count == 0:
            return Response({"pincode": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        # get middle row directly in DB instead of fetching all
        center_obj = qs.select_related("place")[count // 2]

        pincode_obj = (
            PlacePincode.objects.filter(place=center_obj.place).select_related("place").first()
        )

        if not pincode_obj:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlacePincodeSerializer(pincode_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    @action(methods=["GET"], detail=True)
    def get_state(self, request, slug=None):
        state = self.get_object()

        if not state:
            return Response({"state": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)        

        state = UniqueState.objects.filter(slug= state.slug).first()

        if not state:
            return Response({"state": "Not found"}, status=status.HTTP_404_NOT_FOUND)        

        serializer = StateSerializer(state)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DistrictViewset(ReadOnlyModelViewSet):
    queryset = UniqueDistrict.objects.all().order_by("name")
    serializer_class = DistrictSerializer
    lookup_field = "slug"

    @action(methods=["GET"], detail=True)
    def get_center(self, request, slug=None):
        district = self.get_object()

        if not district:
            return Response({"center": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        # Count coordinates first (cheap query)
        total = PlaceCoordinate.objects.filter(place__district=district).count()
        if total == 0:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        index_of_center_obj = total // 2

        # Fetch only the "middle" row instead of loading all
        center_obj = (
            PlaceCoordinate.objects.filter(place__district=district)
            .order_by("latitude", "longitude")
            .values("id")  # we only need id for retrieval
            [index_of_center_obj]
        )

        # Now fetch full object for serialization
        center_instance = PlaceCoordinate.objects.get(id=center_obj["id"])
        serializer = PlaceCoordinateSerializer(center_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    @action(methods=["GET"], detail=True)
    def get_pincode(self, request, slug=None):
        district = self.get_object()

        if not district:
            return Response({"pincode": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        # Try direct match
        pincode_obj = (
            PlacePincode.objects.select_related("place")
            .filter(place__name=district.name)
            .first()
        )
        if pincode_obj:
            return Response(PlacePincodeSerializer(pincode_obj).data, status=status.HTTP_200_OK)

        # Get middle coordinate without loading all
        qs = PlaceCoordinate.objects.filter(place__district=district).order_by("latitude", "longitude")
        count = qs.count()
        if not count:
            return Response({"pincode": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        center_point = qs.values("id", "latitude", "longitude")[count // 2]
        center_obj = PlaceCoordinate.objects.select_related("place").filter(id=center_point["id"]).first()

        pincode_obj = PlacePincode.objects.filter(place=center_obj.place).first() if center_obj else None
        if not center_obj or not pincode_obj:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(PlacePincodeSerializer(pincode_obj).data, status=status.HTTP_200_OK)



class StateDistrictsViewSet(ReadOnlyModelViewSet):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        state_slug = self.kwargs.get("state_slug")

        if state_slug:
            return UniqueDistrict.objects.filter(state__slug = state_slug)
        
        return UniqueDistrict.objects.none()
    

class MinimalDistrictViewSet(ReadOnlyModelViewSet):
    serializer_class = MinimalDistrictSerializer
    queryset = UniqueDistrict.objects.all().select_related("state")
    lookup_field = "slug"
    

class MinimalStateDistrictsViewSet(ReadOnlyModelViewSet):
    serializer_class = MinimalDistrictSerializer

    def get_queryset(self):
        state_slug = self.kwargs.get("state_slug")
        name = self.request.query_params.get("name")

        if state_slug:
            filters = {"state__slug": state_slug}

            if name:
                filters["name"] = name

            return UniqueDistrict.objects.filter(**filters).select_related("state")
        
        return UniqueDistrict.objects.none()


class PlaceViewset(ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.all().select_related(
        "district", "state"
    ).prefetch_related(
        "pincodes", "coordinates"
    ).order_by("name")
    serializer_class = SimplePlaceSerializer
    lookup_field = "slug"

    @action(methods=["GET"], detail=True)
    def get_center(self, request, slug=None):
        place = self.get_object()
        if not place:
            return Response({"center": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        qs = PlaceCoordinate.objects.filter(place=place).order_by("id")

        count = qs.count()
        if count == 0:
            return Response({"center": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        index_of_center_obj = count // 2
        center_obj = qs[index_of_center_obj] 

        serializer = PlaceCoordinateSerializer(center_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DistrictPlacesViewset(ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.all().order_by("name")
    serializer_class = SimplePlaceSerializer

    def get_queryset(self):
        district_slug = self.kwargs.get("district_slug")

        if district_slug:
            return UniquePlace.objects.filter(district__slug = district_slug)
        
        return UniquePlace.objects.none()


class StateCourseMultiPageViewSet(ReadOnlyModelViewSet):
    serializer_class = MultiPageSerializer
    lookup_field = "slug"
    pagination_class = CourseMultipagePagination

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")

        place_slug = self.request.query_params.get("place_slug")
        state_slug = self.request.query_params.get("state_slug")
        district_slug = self.request.query_params.get("district_slug")
        specialization_slug = self.request.query_params.get("specialization")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})
        
        if slug == "all" or slug == "india":
            return MultiPage.objects.select_related(
                "company", "course", "course__program",
                "course__specialization"
                ).prefetch_related(
                    "features", 
                    "vertical_tabs", 
                    "horizontal_tabs", 
                    "tables", 
                    "bullet_points", 
                    "timelines", 
                    "meta_tags",
                    "faqs",
                    "text_editors",
                    "slider_courses",
                )
        
        state = None
        district = None

        if place_slug:
            place = get_object_or_404(UniquePlace, slug=slug)
            district = place.district
            state = place.state
        elif district_slug:
            district = get_object_or_404(UniqueDistrict, slug=slug)
            state = district.state
        else:
            state = get_object_or_404(UniqueState, slug=slug)

        if state_slug and state_slug != state.slug:            
            return MultiPage.objects.none()

        if district_slug and district_slug != district.slug:
            return MultiPage.objects.none()
        
        filters = {"available_states": state}

        if specialization_slug:
            filters["course__specialization__slug"] = specialization_slug

        return MultiPage.objects.filter(
            **filters
            ).select_related(
                "company", "course", "course__program",
                "course__specialization"
            ).prefetch_related(
                "features", 
                "vertical_tabs", 
                "horizontal_tabs", 
                "tables", 
                "bullet_points", 
                "timelines", 
                "meta_tags",
                "faqs",
                "text_editors",
                "slider_courses",
            )
    

class StateRegistrationMultiPageViewSet(ReadOnlyModelViewSet):
    serializer_class = RegistrationMultipageSerializer
    lookup_field = "slug"
    pagination_class = RegistrationMultipagePagination

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")

        place_slug = self.request.query_params.get("place_slug")
        state_slug = self.request.query_params.get("state_slug")
        district_slug = self.request.query_params.get("district_slug")
        sub_type_slug = self.request.query_params.get("sub_type")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})
        
        if slug == "all" or slug == "india":
            return RegistrationMultiPage.objects.all().select_related(
                "company", "registration", "registration__sub_type",
                "registration__registration_type"
                ).prefetch_related(
                    "features", 
                    "vertical_tabs", 
                    "horizontal_tabs", 
                    "tables", 
                    "bullet_points", 
                    "timelines", 
                    "meta_tags",
                    "faqs",
                    "text_editors",
                    "slider_registrations",
                )

        state = None
        district = None

        if place_slug:
            place = get_object_or_404(UniquePlace, slug=slug)
            district = place.district
            state = place.state
        elif district_slug:
            district = get_object_or_404(UniqueDistrict, slug=slug)
            state = district.state
        else:
            state = get_object_or_404(UniqueState, slug=slug)

        if state_slug and state_slug != state.slug:
            return RegistrationMultiPage.objects.none()

        if district_slug and district_slug != district.slug:
            return RegistrationMultiPage.objects.none()
        
        filters = {
            "available_states": state
        }

        if sub_type_slug:
            filters["registration__sub_type__slug"] = sub_type_slug

        return RegistrationMultiPage.objects.filter(
            **filters
            ).select_related(
                "company", "registration", "registration__sub_type",
                "registration__registration_type"
            ).prefetch_related(
                "features", 
                "vertical_tabs", 
                "horizontal_tabs", 
                "tables", 
                "bullet_points", 
                "timelines", 
                "meta_tags",
                "faqs",
                "text_editors",
                "slider_registrations",
            )
    

class StateProductMultiPageViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductMultipageSerializer
    lookup_field = "slug"
    pagination_class = ProductMultipagePagination

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")
        
        place_slug = self.request.query_params.get("place_slug")
        state_slug = self.request.query_params.get("state_slug")
        district_slug = self.request.query_params.get("district_slug")
        sub_category_slug = self.request.query_params.get("sub_category")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})
        
        if slug == "all" or slug == "india":
            return ProductMultiPage.objects.all().select_related(
                "company"
            ).prefetch_related(
                "products",
                "features",                     
                "bullet_points", 
                "timelines", 
                "meta_tags",
                "faqs",
                "text_editors",
            )

        state = None
        district = None

        if place_slug:
            place = get_object_or_404(UniquePlace, slug=slug)
            district = place.district
            state = place.state
        elif district_slug:
            district = get_object_or_404(UniqueDistrict, slug=slug)
            state = district.state
        else:
            state = get_object_or_404(UniqueState, slug=slug)

        if state_slug and state_slug != state.slug:
            return ProductMultiPage.objects.none()

        if district_slug and district_slug != district.slug:
            return ProductMultiPage.objects.none()
        
        filters = {"available_states": state}

        if sub_category_slug:
            filters["products__sub_category__slug"] = sub_category_slug

        return ProductMultiPage.objects.filter(
            **filters
        ).select_related(
            "company"
        ).prefetch_related(
            "products",
            "features",                     
            "bullet_points", 
            "timelines", 
            "meta_tags",
            "faqs",
            "text_editors",
        )

# class LocationMatchViewSet(ReadOnlyModelViewSet):
#     queryset = UniquePlace.objects.none()
#     serializer_class = PlaceSerializer

#     def retrieve(self, request, *args, **kwargs):        
#         slug = self.kwargs.get("slug")

#         location_type = self.kwargs.get("location_type")   

#         for model_type, get_trie_fn, model, serializer_class in MATCH_ORDER:
#             if location_type and location_type != "undefined" and model_type != location_type:
#                 continue
#             trie = get_trie_fn()
#             matched_slug = trie.match_suffix(slug)
#             if matched_slug:
#                 try:
#                     instance = model.objects.get(slug=matched_slug)

#                     serializer = serializer_class(instance)
#                     return Response({
#                         "match_type": model_type,
#                         "data": serializer.data
#                     })
#                 except model.DoesNotExist:
#                     return Response({
#                         "match_type": model_type,
#                         "matched_slug": matched_slug,
#                         "warning": "Slug matched in trie but not found in DB."
#                     })                                            

#         return Response({"match_type": None, "matched_slug": None})

MATCH_ORDER = [
    ("state", get_state_trie, UniqueState, MiniStateSerializer),
    ("district", get_district_trie, UniqueDistrict, DistrictMiniSerializer),
    ("place", get_place_trie, UniquePlace, PlaceMiniSerializer),
]

class LocationMatchViewSet(ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.none()
    serializer_class = PlaceSerializer

    def retrieve(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        location_type = self.kwargs.get("location_type")

        best_match = {
            "model_type": None,
            "matched_slug": None,
            "match_length": 0,
            "serializer_class": None,
        }

        for model_type, get_trie_fn, model, serializer_class in MATCH_ORDER:            
            if location_type and location_type != "undefined" and model_type != location_type:
                continue

            matched_slug = get_trie_fn().match_suffix(slug)
            if not matched_slug:
                continue

            match_length = len(matched_slug)
            current_index = next((i for i, (t, *_r) in enumerate(MATCH_ORDER) if t == model_type), -1)
            best_index = next((i for i, (t, *_r) in enumerate(MATCH_ORDER) if t == best_match["model_type"]), -1)

            is_better = (
                match_length > best_match["match_length"]
                or (match_length == best_match["match_length"] and current_index > best_index)
            )

            if is_better:
                best_match.update({
                    "model_type": model_type,
                    "matched_slug": matched_slug,
                    "match_length": match_length,
                    "serializer_class": serializer_class,
                })

        # Get the instance only for the final best match
        final_instance = None
        if best_match["matched_slug"]:
            model = next((m for t, _, m, _ in MATCH_ORDER if t == best_match["model_type"]), None)
            if model:
                final_instance = model.objects.filter(slug=best_match["matched_slug"]).first()

        if final_instance:
            serializer = best_match["serializer_class"](final_instance)
            return Response({
                "match_type": best_match["model_type"],
                "data": serializer.data,
            })

        return Response({
            "match_type": best_match["model_type"],
            "matched_slug": best_match["matched_slug"],
            "warning": "Matched in trie but not found in DB." if best_match["matched_slug"] else "No match found."
        })


    

class StateServiceMultiPageViewSet(ReadOnlyModelViewSet):
    serializer_class = ServiceMultipageSerializer
    lookup_field = "slug"
    pagination_class = ServiceMultipagePagination

    def get_queryset(self):
        slug = self.kwargs.get("state_slug")

        sub_category_slug = self.request.query_params.get("sub_category")

        if not slug:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Slug was not provided"})

        if slug == "all" or slug == "india":
            return ServiceMultiPage.objects.select_related(
                "company", "service", "service__category",
                "service__sub_category"
                ).prefetch_related(
                    "features", 
                    "vertical_tabs", 
                    "horizontal_tabs", 
                    "tables", 
                    "bullet_points", 
                    "timelines", 
                    "meta_tags",
                    "faqs",
                    "text_editors",
                    "slider_services",
                )

        state = get_object_or_404(UniqueState, slug=slug)

        filters = {"available_states": state}

        if sub_category_slug:
            filters["service__sub_category__slug"] = sub_category_slug

        return ServiceMultiPage.objects.filter(
            **filters
            ).select_related(
                "company", "service", "service__category",
                "service__sub_category"
            ).prefetch_related(
                "features", 
                "vertical_tabs", 
                "horizontal_tabs", 
                "tables", 
                "bullet_points", 
                "timelines", 
                "meta_tags",
                "faqs",
                "text_editors",
                "slider_services",
            )


class PopularCityViewSet(ReadOnlyModelViewSet):
    serializer_class = MiniPlaceSerializer

    def get_queryset(self):        

        popular_cities = [
            "Mumbai", "Bengaluru", "Hyderabad", "Kolkata", "Chennai", "Pune", "Ahmedabad", "Surat", "Jaipur", "Lucknow", "Kanpur", 
            "Indore", "Patna", "Nagpur", "Visakhapatnam", "Meerut", "Bhopal", "Varanasi", "Agra", "Nashik", "Guwahati", "Rajkot", 
            "Warangal", "Coimbatore", "Thiruvananthapuram", "Faridabad", "Ghaziabad", "Chandigarh", "Ludhiana", "Vadodara", "Raipur", 
            "Jodhpur", "Gwalior", "Tiruchirappalli", "Jamshedpur", "Ranchi", "Prayagraj", "Jalandhar", "Jabalpur", "Asansol", 
            "Gurugram", "Mysuru", "Kochi", "Amritsar", "Agartala", "Ajmer", "Aligarh", "Prayagraj", "Ambala", "Amravati", "Anantapur", 
            "Aurangabad", "Bareilly", "Belagavi", "Bharuch", "Bhilai", "Bhubaneshwar", "Bilaspur", "Bokaro", "Cuttack", "Darbhanga", 
            "Dehradun", "Dhanbad", "Durgapur", "Erode", "Gandhinagar", "Gaya", "Gorakhpur", "Kalaburagi", "Guntur", "Hisar", "Hubballi", 
            "Imphal", "Jammu", "Kannur", "Kolhapur","Kollam", "Kozhikode", "Madurai", "Salem", "Siliguri", "Thrissur", "Tirunelveli", 
            "Vijayawada"
        ]        

        subquery = UniquePlace.objects.filter(
            name=OuterRef("name")
        ).order_by("created").values("pk")[:1]

        qs = UniquePlace.objects.filter(
            name__in=popular_cities,
            pk=Subquery(subquery)
        ).select_related("state", "district")

        # preserve the same order as popular_cities
        place_map = {obj.name: obj for obj in qs}
        return [place_map[city] for city in popular_cities if city in place_map]


class MinimalDistrictPlaceViewset(ReadOnlyModelViewSet):
    queryset = UniquePlace.objects.none()
    serializer_class = MinimalPlaceSerializer

    def get_queryset(self):
        district_slug = self.kwargs.get("district_slug")
        name = self.request.query_params.get("name")

        if district_slug:
            filters = {"district__slug": district_slug}

            if name:
                filters["name"] = name

            return UniquePlace.objects.filter(**filters)
        
        return UniquePlace.objects.none()
    

class MinimalPlaceViewset(ReadOnlyModelViewSet):
    serializer_class = MinimalPlaceSerializer
    queryset = UniquePlace.objects.all().select_related("state", "district")
    lookup_field = "slug"
