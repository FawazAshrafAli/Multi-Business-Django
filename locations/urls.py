from django.urls import path
from .views import generate_location_csv, get_districts, get_places

app_name = "locations"

urlpatterns = [
    path('', generate_location_csv, name="generate_csv"),
    path('get_districts/', get_districts, name="get_districts"),
    path('get_places/', get_places, name="get_places"),
]
