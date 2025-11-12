from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    GetNearbyLocationsViewSet, StateViewset, MinimalDistrictViewSet,
    StateCourseMultiPageViewSet, DistrictViewset, GetNearestLocationViewSet,
    StateRegistrationMultiPageViewSet, PlaceViewset, LocationMatchViewSet,
    StateProductMultiPageViewSet, StateServiceMultiPageViewSet,
    StateDistrictsViewSet, DistrictPlacesViewset, MinimalDistrictPlaceViewset,
    PopularCityViewSet, MinimalStateViewset, MinimalStateDistrictsViewSet,
    MinimalPlaceViewset
    )

app_name = "location_api"

router = DefaultRouter()

router.register(r'states', StateViewset, basename="state")
router.register(r'minimal-states', MinimalStateViewset, basename="minimal-state")
router.register(r'minimal-districts', MinimalDistrictViewSet, basename="minimal-district")
router.register(r'minimal-places', MinimalPlaceViewset, basename="minimal-place")
router.register(r'districts', DistrictViewset, basename="district")
router.register(r'places', PlaceViewset, basename="place")
router.register(r'nearby_locations', GetNearbyLocationsViewSet, basename="location")
router.register(r'popular_cities', PopularCityViewSet, basename="popular_city")

states_router = NestedDefaultRouter(router, r'states', lookup="state")

states_router.register(r'course_multipages', StateCourseMultiPageViewSet, basename="state-course_multipage")
states_router.register(r'registration_multipages', StateRegistrationMultiPageViewSet, basename="state-registration_multipage")
states_router.register(r'product_multipages', StateProductMultiPageViewSet, basename="state-product_multipage")
states_router.register(r'service_multipages', StateServiceMultiPageViewSet, basename="state-service_multipage")
states_router.register(r'districts', StateDistrictsViewSet, basename="state-district")
states_router.register(r'minimal-districts', MinimalStateDistrictsViewSet, basename="state-minimal-district")

districts_router = NestedDefaultRouter(router, r'districts', lookup="district")

districts_router.register(r'places', DistrictPlacesViewset, basename="district-place")
districts_router.register(r'minimal-places', MinimalDistrictPlaceViewset, basename="district-minimal-place")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(states_router.urls)),
    path('', include(districts_router.urls)),
    path('nearest_place/', GetNearestLocationViewSet.as_view({"get":"get"})),
    path('get_location/<str:location_type>/<str:slug>/', LocationMatchViewSet.as_view({"get":"retrieve"}), name="get_location"),
]
