import os
from django.conf import settings
from django.http import HttpRequest
from geoip2.database import Reader
from ipware import get_client_ip

from locations.models import PlaceCoordinate, UniquePlace

def get_ip_location(request: HttpRequest):
    ip, _ = get_client_ip(request)
    if not ip:
        return None
    
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "103.25.204.10")

    # Path to the GeoLite2-City.mmdb file
    db_path = os.path.join(settings.BASE_DIR, 'geoip', 'GeoLite2-City.mmdb')

    try:
        reader = Reader(db_path)
        response = reader.city(ip)

        # return {
        #     "ip": ip,
        #     "country": response.country.name,
        #     "region": response.subdivisions.most_specific.name,
        #     "city": response.city.name,
        #     "latitude": response.location.latitude,
        #     "longitude": response.location.longitude,
        # }

        return {            
            "latitude": response.location.latitude,
            "longitude": response.location.longitude,
        }

    except Exception as e:
        return None
    finally:
        reader.close()


def get_nearby_locations(lat, lon):
    try:    
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return PlaceCoordinate.objects.none()

    difference = 0.05

    start_lat = lat - difference
    start_lon = lon - difference

    end_lat = lat + difference
    end_lon = lon + difference

    starting_point = [start_lat, start_lon]
    ending_point = [end_lat, end_lon]

    unfiltered_places = PlaceCoordinate.objects.filter(
        latitude__range=(starting_point[0], ending_point[0]),
        longitude__range=(starting_point[1], ending_point[1])
    )

    unique_places_dict = dict()
    for place_obj in unfiltered_places:
        unique_places_dict[place_obj.place.name] = place_obj.place.slug

    return UniquePlace.objects.filter(slug__in = unique_places_dict.values()).select_related("district", "state")


from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import re

def detect_script(text):
    """Detect script based on Unicode range of characters."""
    for char in text:
        code = ord(char)
        if 0x0900 <= code <= 0x097F:
            return sanscript.DEVANAGARI
        elif 0x0B80 <= code <= 0x0BFF:
            return sanscript.TAMIL
        elif 0x0C00 <= code <= 0x0C7F:
            return sanscript.TELUGU
        elif 0x0C80 <= code <= 0x0CFF:
            return sanscript.KANNADA
        elif 0x0D00 <= code <= 0x0D7F:
            return sanscript.MALAYALAM
        elif 0x0980 <= code <= 0x09FF:
            return sanscript.BENGALI
        elif 0x0A80 <= code <= 0x0AFF:
            return sanscript.GUJARATI
        elif 0x0B00 <= code <= 0x0B7F:
            return sanscript.ORIYA
        elif 0x0A00 <= code <= 0x0A7F:
            return sanscript.GURMUKHI
    return None

def transliterate_place_name(text):
    script = detect_script(text)
    if not script:
        print("⚠️ Script could not be detected.")
        return text  # Return original if detection failed

    try:
        raw_output = transliterate(text, script, sanscript.ITRANS)
    except Exception as e:
        print(f"⚠️ Transliteration failed: {e}")
        return text

    simplified = raw_output.lower()
    simplified = re.sub(r'([a-z])\1+', r'\1', simplified)  # reduce double letters
    simplified = re.sub(r'[^a-z]', '', simplified)         # remove special characters

    return simplified