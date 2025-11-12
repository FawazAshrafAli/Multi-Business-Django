from ..models import IndiaLocationData, PincodeAndCoordinate, UniquePlace

def get_opencage_pincode_and_coordiante(json_item):
    results = json_item.get("results")
    if not results:
        return {"pincode": None, "latitude": None, "longitude": None}

    result = results[0]
    components = result.get("components", {})
    coordinate = result.get("geometry", {})

    pincode = components.get("postcode")
    latitude = coordinate.get("lat")
    longitude = coordinate.get("lng")

    return {
        "pincode": pincode,
        "latitude": latitude,
        "longitude": longitude
    }


def update_pincodes():
    import logging
    from ..models import PlacePincode, PlaceCoordinate

    logger = logging.getLogger(__name__)

    opencage_collection = IndiaLocationData.objects.all()
    post_office_collection = PincodeAndCoordinate.objects.all()

    opencage_place_slugs = set(opencage_collection.values_list("place__slug", flat=True))
    post_office_place_slugs = set(post_office_collection.values_list("place__slug", flat=True))

    updating_place_slugs = opencage_place_slugs | post_office_place_slugs
    modifying_places = UniquePlace.objects.filter(slug__in=updating_place_slugs)

    places_length = len(modifying_places)
    progress = 0

    for index, place in enumerate(modifying_places):
        current_progress = int((index + 1) * 100 / places_length)

        if current_progress > progress:
            progress = current_progress
            logger.info(f"{current_progress}% Completed")

        pincodes = []
        latitude = None
        longitude = None

        if place.slug in opencage_place_slugs:
            for item in opencage_collection.filter(place__slug=place.slug):
                place_data = get_opencage_pincode_and_coordiante(item)
                pincode = place_data.get("pincode")
                latitude = latitude or place_data.get("latitude")
                longitude = longitude or place_data.get("longitude")
                if pincode:
                    pincodes.append(pincode)

        if place.slug in post_office_place_slugs:
            for item in post_office_collection.filter(place__slug=place.slug):
                pincode = item.pincode
                latitude = latitude or item.latitude
                longitude = longitude or item.longitude
                if pincode:
                    pincodes.append(pincode)

        pincodes = set(pincodes)

        if pincodes:
            PlacePincode.objects.filter(place=place).delete()
            PlacePincode.objects.bulk_create([
                PlacePincode(place=place, pincode=p) for p in pincodes
            ])

        if latitude and longitude:
            PlaceCoordinate.objects.filter(place=place).delete()
            PlaceCoordinate.objects.create(
                place=place, latitude=latitude, longitude=longitude
            )

        place.pincodes.set(PlacePincode.objects.filter(place=place))
        place.coordinates.set(PlaceCoordinate.objects.filter(place=place))

        logger.info(f"Updated {place.name} ({place.slug})")
