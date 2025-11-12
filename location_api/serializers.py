from rest_framework import serializers

from locations.models import UniquePlace, UniqueState, UniqueDistrict, PlaceCoordinate, PlacePincode

class PlaceCoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceCoordinate
        fields = ["latitude", "longitude"]


class PlacePincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacePincode
        fields = ["pincode"]


class DistrictMiniSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source="state.name", read_only=True)
    state_slug = serializers.CharField(source="state.slug", read_only=True)
    pincode = serializers.CharField(source="get_pincode", read_only = True)
    latitude = serializers.CharField(source="get_latitude", read_only = True)
    longitude = serializers.CharField(source="get_longitude", read_only = True)

    class Meta:
        model = UniqueDistrict
        fields = [
            "name", "slug", "updated", "state_name", "state_slug",
            "latitude", "longitude", "pincode"
                  ]


class MinimalDistrictSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source = "state.name")
    state_slug = serializers.CharField(source = "state.slug")

    class Meta:
        model = UniqueDistrict
        fields = ["name", "slug", "state_name", "state_slug", "updated"]


class StateSerializer(serializers.ModelSerializer):
    districts = MinimalDistrictSerializer(many=True, read_only = True)

    class Meta:
        model = UniqueState
        fields = ["name", "slug", "districts", "updated"]


class MinimalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueState
        fields = ["name", "slug", "updated"]




class MiniStateSerializer(serializers.ModelSerializer):
    pincode = serializers.CharField(source="get_pincode", read_only=True)
    latitude = serializers.CharField(source="get_latitude", read_only=True)
    longitude = serializers.CharField(source="get_longitude", read_only=True)

    class Meta:
        model = UniqueState
        fields = ["name", "slug", "updated", "pincode", "latitude", "longitude"]


class MinimalPlaceSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)
    district_slug = serializers.CharField(source="district.slug", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    state_slug = serializers.CharField(source="state.slug", read_only=True) 
    pincode = serializers.CharField(source="get_pincode", read_only=True)  

    class Meta:
        model = UniquePlace
        fields = [
            "name", "slug", "updated", "district_name", "district_slug", 
            "state_name", "state_slug", "pincode"
            ]

class PlaceMiniSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)
    district_slug = serializers.CharField(source="district.slug", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    state_slug = serializers.CharField(source="state.slug", read_only=True)   
    pincode = serializers.CharField(source="get_pincode", read_only=True)
    latitude = serializers.CharField(source="get_latitude", read_only=True)
    longitude = serializers.CharField(source="get_longitude", read_only=True)

    class Meta:
        model = UniquePlace
        fields = [
            "name", "slug", "updated", "district_name", "district_slug", 
            "state_name", "state_slug", "pincode", "latitude", "longitude"
            ]

        
class DistrictSerializer(serializers.ModelSerializer):
    places = MinimalPlaceSerializer(many=True, read_only = True)
    state = MinimalStateSerializer()
    slug = serializers.SlugField()

    class Meta:
        model = UniqueDistrict
        fields = ["name", "slug", "state", "places", "updated"]    


class MiniPlaceSerializer(serializers.ModelSerializer):    
    state_name = serializers.CharField(source="state.name", read_only=True)
    state_slug = serializers.CharField(source="state.slug", read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    district_slug = serializers.CharField(source="district.slug", read_only=True)    

    class Meta:
        model = UniquePlace
        fields = ["name", "slug", "state_name", "state_slug", "district_name", "district_slug"]


class PlaceSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    district = DistrictSerializer()
    coordinates = PlaceCoordinateSerializer(many=True, read_only=True)
    pincodes = PlacePincodeSerializer(many=True, read_only=True)

    class Meta:
        model = UniquePlace
        fields = ["name", "pincodes", "coordinates", "slug", "state", "district", "updated"]



class SimplePlaceSerializer(serializers.ModelSerializer):
    district = MinimalDistrictSerializer()
    state = MinimalStateSerializer()
    coordinates = PlaceCoordinateSerializer(many=True, read_only=True)
    pincodes = PlacePincodeSerializer(many=True)

    class Meta:
        model = UniquePlace
        fields = ["name", "slug", "district", "state", "coordinates", "pincodes", "updated"]


class BasePlaceSerializer(serializers.ModelSerializer):
    district = MinimalDistrictSerializer()
    state = MinimalStateSerializer()    

    class Meta:
        model = UniquePlace
        fields = ["name", "slug", "district", "state", "updated"]
