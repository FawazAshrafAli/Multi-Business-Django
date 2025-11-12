from rest_framework import serializers

from directory.models import CscCenter
from registration.models import RegistrationSubType
from registration_api.serializers import SubTypeSerializer
from locations.models import UniqueDistrict, UniqueState

class MinimalCscCenterSerializer(serializers.ModelSerializer):   
    district = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:        
        model = CscCenter
        fields = [
            "name", "slug", "place_name", "district_name",
            "state_name", "title", "all_registrations",
            "pincode", "contact_number", "latitude", 
            "longitude", "district", "state"
        ] 

    def get_district(self, obj):
        if not hasattr(obj, "district_name") or not (hasattr(obj, "state_name")): return None

        district = UniqueDistrict.objects.filter(name = obj.district_name, state__name = obj.state_name).first()

        return {"name": district.name, "slug": district.slug} if district else None

    def get_state(self, obj):
        if not hasattr(obj, "state_name"): return None

        state = UniqueState.objects.filter(name = obj.state_name).first()

        return {"name": state.name, "slug": state.slug} if state else None


class CscSerializer(serializers.ModelSerializer):    
    registrations = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:        
        model = CscCenter
        fields = [
            "name", "slug", "place_name", "district_name",
            "state_name", "title", "all_registrations",
            "pincode", "contact_number", "latitude", 
            "longitude", "street", "location", "contact_number",
            "mobile_number", "whatsapp_number", "email",
            "district", "state", "registrations", "created",
            "updated"
        ]     
    
    def get_registrations(self, obj):
        if not hasattr(obj, "all_registrations"):
            return []
        
        registrations_string = obj.all_registrations

        if not registrations_string: return []
        
        registrations_list = registrations_string.split(',')
        unique_registrations_list = list(set(registrations_list))

        registrations = RegistrationSubType.objects.filter(
            name__in = unique_registrations_list
        )

        serializers = SubTypeSerializer(registrations, many=True)

        return serializers.data
    
    def get_district(self, obj):
        if not hasattr(obj, "district_name") or not (hasattr(obj, "state_name")): return None

        district = UniqueDistrict.objects.filter(name = obj.district_name, state__name = obj.state_name).first()

        return {"name": district.name, "slug": district.slug} if district else None
    
    def get_state(self, obj):
        if not hasattr(obj, "state_name"): return None

        state = UniqueState.objects.filter(name = obj.state_name).first()

        return {"name": state.name, "slug": state.slug} if state else None