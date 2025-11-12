from django.contrib import admin
from .models import IndianLocation

class IndianLocationAdmin(admin.ModelAdmin):
    list_display = [
        "state", "state_code", "district", "county", "city", "town", 
        "village", "suburb", "city_district", "postcode", "place_type", 
        "latitude", "longitude"
    ]

admin.site.register(IndianLocation, IndianLocationAdmin)
