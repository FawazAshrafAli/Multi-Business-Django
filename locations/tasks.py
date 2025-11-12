import logging
from locations.views import get_india_locations
from celery import shared_task
import os

from locations.models import PincodeAndCoordinate, IndiaLocationData, UniquePlace
from directory.views import fetch_destination_locations, logger, fetch_police_locations, fetch_court_locations

def configure_logger(log_filename):
    logger = logging.getLogger(log_filename)
    if not logger.hasHandlers():  # Prevent duplicate handlers
        handler = logging.FileHandler(log_filename, mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


@shared_task(queue="worker1_queue")
def run1():
    logger = configure_logger("run1.log")
    logger.info("Starting run1 (India Stage 1)\n")

    # Stage 1
    top_left = (37.1, 68.1)
    bottom_right = (27.4, 97.5)

    top_left = (30.89, 68.1)

    api_key = os.getenv('OPENCAGE_API_KEY_1')
    opencage_cache = "opencage_requested_1"

    get_india_locations(top_left, bottom_right, api_key, opencage_cache)

@shared_task(queue="worker2_queue")
def run2():
    logger = configure_logger("run2.log")
    logger.info("Starting run2 (India Stage 2)\n")

    # Stage 2
    top_left = (27.4, 68.1)
    bottom_right = (17.7, 97.5) 

    top_left = (23.32, 68.1)

    api_key = os.getenv('OPENCAGE_API_KEY_2')
    opencage_cache = "opencage_requested_2"

    get_india_locations(top_left, bottom_right, api_key, opencage_cache)

@shared_task(queue="worker3_queue")
def run3():
    logger = configure_logger("run3.log")
    logger.info("Starting run3 (India Stage 3)\n")

    # Stage 3
    top_left = (17.7, 68.1)
    bottom_right = (8.0, 97.5)

    top_left = (12.6, 68.1)

    api_key = os.getenv('OPENCAGE_API_KEY_3')
    opencage_cache = "opencage_requested_3"

    get_india_locations(top_left, bottom_right, api_key, opencage_cache)

@shared_task(bind=True, queue="worker1_queue", autoretry_for=(Exception,), retry_backoff=10, max_retries=5)
def fetch_locations_1(self):    
    logger.info("Starting destination location fetching task via Celery")       
    try:
        fetch_destination_locations()
        logger.info("Destination location fetching task completed successfully")
    except Exception as e:
        logger.error(f"Destination location fetching task failed: {e}")
        raise e
    

@shared_task(bind=True, queue="worker2_queue", autoretry_for=(Exception,), retry_backoff=10, max_retries=5)
def fetch_locations_2(self):
    logger.info("Starting police location fetching task via Celery")
    try:
        fetch_police_locations()
        logger.info("Police location fetching task completed successfully")
    except Exception as e:
        logger.error(f"Police location fetching task failed: {e}")
        raise e
    
@shared_task(bind=True, queue="worker3_queue", autoretry_for=(Exception,), retry_backoff=10, max_retries=5)
def fetch_locations_3(self):
    logger.info("Starting court location fetching task via Celery")
    try:
        fetch_court_locations()
        logger.info("Court location fetching task completed successfully")
    except Exception as e:
        logger.error(f"Court location fetching task failed: {e}")
        raise e

@shared_task(queue="worker5_queue")
def update_places(selected_state):
    from collections import defaultdict
    from django.db import transaction

    from locations.models import UniquePlace, PlaceCoordinate, PlacePincode, Place

    # Step 1: Index all Place records in memory
    logger.info(f"Loading all Place of {selected_state} into memory...")
    place_index = defaultdict(lambda: {"pincodes": set(), "coordinates": set()})
    for pl in Place.objects.filter(state__name = selected_state).select_related("district", "state").values(
        "name", "district__name", "state__name", "pincode", "latitude", "longitude"
    ):
        key = (pl["name"], pl["district__name"], pl["state__name"])
        place_index[key]["pincodes"].add(pl["pincode"])
        place_index[key]["coordinates"].add((pl["latitude"], pl["longitude"]))

    logger.info(f"Indexed {len(place_index)} place groups.")

    # Step 2: Process UniquePlaces with minimal DB hits
    unique_places = UniquePlace.objects.select_related("district", "state").prefetch_related("pincodes", "coordinates")

    new_pincodes = []
    new_coordinates = []
    place_pincode_map = defaultdict(list)
    place_coordinate_map = defaultdict(list)

    logger.info("Processing UniquePlaces...")
    for place in unique_places:
        key = (place.name, place.district.name, place.state.name)
        data = place_index.get(key)
        if not data:
            continue

        for pincode in data["pincodes"]:
            new_pincodes.append(PlacePincode(place=place, pincode=pincode))
            place_pincode_map[place].append(pincode)

        for lat, lng in data["coordinates"]:
            new_coordinates.append(PlaceCoordinate(place=place, latitude=lat, longitude=lng))
            place_coordinate_map[place].append((lat, lng))

    logger.info("Bulk creating PlacePincode and PlaceCoordinate objects...")

    # Step 3: Bulk create (ignore duplicates)
    with transaction.atomic():
        PlacePincode.objects.bulk_create(new_pincodes, ignore_conflicts=True)
        PlaceCoordinate.objects.bulk_create(new_coordinates, ignore_conflicts=True)

    logger.info("Re-fetching created pincode and coordinate objects...")

    # Step 4: Re-fetch related objects to set M2M
    pincode_objs = PlacePincode.objects.filter(place__in=unique_places)
    coordinate_objs = PlaceCoordinate.objects.filter(place__in=unique_places)

    pincode_lookup = defaultdict(list)
    for pp in pincode_objs:
        pincode_lookup[pp.place_id].append(pp)

    coordinate_lookup = defaultdict(list)
    for pc in coordinate_objs:
        coordinate_lookup[pc.place_id].append(pc)

    logger.info("Updating M2M relations in bulk...")
    for place in unique_places:
        place.pincodes.set(pincode_lookup[place.id])
        place.coordinates.set(coordinate_lookup[place.id])

    logger.info("Update complete.")


@shared_task(queue="worker4_queue")
def fetch_pincode_and_coordinate():
    from directory.models import PostOffice
    from .models import UniquePlace, PincodeAndCoordinate
    from django.db.models import Count

    logger.info("Program Started.")

    places = list(
        UniquePlace.objects.annotate(
            pincode_count=Count("pincodes")
        ).filter(
            pincode_count__gt=1            
        )
    )

    places_length = len(places)

    logger.info(f"Found {len(places)} places having more than a single pincode.")

    creating_items = []
    progress = 0

    logger.info("Checking for matching post offices...")

    for index, place in enumerate(places):
        current_progress = int((index + 1) * 100 / places_length)

        if current_progress > progress:
            progress = current_progress
            logger.info(f"{current_progress}% Completed")

        try:
            post_offices = PostOffice.objects.filter(
                office_name__icontains=place.name,
                district=place.district.name,
                state_name=place.state.name
            )

            for post_office in post_offices:
                if PincodeAndCoordinate.objects.filter(place = place, pincode = post_office.pincode).exists():
                    continue
                
                latitude = post_office.latitude
                longitude = post_office.longitude

                if latitude:
                    latitude=float(str(post_office.latitude).strip().strip("-"))

                if longitude:
                    longitude=float(str(post_office.longitude).strip().strip("-"))

                creating_items.append(PincodeAndCoordinate(
                    place = place,
                    post_office_id=post_office.id,
                    pincode=post_office.pincode,
                    latitude=latitude,
                    longitude=longitude
                ))

        except PostOffice.DoesNotExist:
            pass

    logger.info(f"\nFound {len(creating_items)} matching post offices.")
    logger.info("Running bulk creation...")

    PincodeAndCoordinate.objects.bulk_create(creating_items, ignore_conflicts=True)

    logger.info("Program Completed.")


def get_indian_locations(places_ids, api_key, opencage_cache):
    from django.db import transaction
    from django.core.cache import cache
    import time
    import requests

    base_url = 'https://api.opencagedata.com/geocode/v1/json'
    request_count = cache.get(opencage_cache, 0)

    places = UniquePlace.objects.filter(id__in = places_ids)

    for place in places:
        if request_count <= 10000:
            with transaction.atomic():
                try:
                    logger.info(f"Querying place: {place.name},{place.district.name},{place.state.name},India")

                    response = requests.get(base_url, params={
                        "q": f"{place.name},{place.district.name},{place.state.name},India",
                        "key": api_key
                    })

                    response.raise_for_status()

                    request_count += 1
                    cache.set(opencage_cache, request_count, timeout=60*60*24)
                    data = response.json()

                    logger.info(f"Request number: {request_count}")

                    if "results" in data and data["results"]:
                        first_result = data["results"][0]
                        components = first_result.get("components", {})
                        formatted = first_result.get("formatted", "")

                        country = components.get("country")                    

                        if str(country).lower() in {"india"}:
                            road = components.get("road")
                            address = formatted.replace(f"{road},", "").strip() if road else formatted

                            IndiaLocationData.objects.create(                                        
                                address = address, json_data = data, place = place                                            
                            )

                            logger.info(f"Location fetched for: '{address}'\n")
                    

                except requests.exceptions.RequestException as e:
                    logger.info(f"Error during API request: {e}")
                    time.sleep(2)
                    continue

                except Exception as e:
                    logger.exception(f"An Unexpected Error occured: {e}")
                    time.sleep(2)
                    continue
        
                time.sleep(0.2)

        else:
            logger.info("You have used up your daily API call limit.")
            return
    
    logger.info("Fetching Completed")

@shared_task(queue="worker1_queue")
def run_india1(place_ids): 
    api_key = os.getenv('OPENCAGE_API_KEY_1')
    opencage_cache = "opencage_requested_1"
    
    get_indian_locations(place_ids, api_key, opencage_cache)

@shared_task(queue="worker2_queue")
def run_india2(place_ids):    
    api_key = os.getenv('OPENCAGE_API_KEY_2')
    opencage_cache = "opencage_requested_2"
    
    get_indian_locations(place_ids, api_key, opencage_cache)

@shared_task(queue="worker3_queue")
def run_india3(place_ids):    
    api_key = os.getenv('OPENCAGE_API_KEY_3')
    opencage_cache = "opencage_requested_3"
    
    get_indian_locations(place_ids, api_key, opencage_cache)

def run_place_fetching():    
    from django.db.models import Count    

    po_places_ids = list(PincodeAndCoordinate.objects.values_list("place__id", flat=True))
    json_place_ids = list(IndiaLocationData.objects.values_list("place__id", flat=True))

    excluding_places_ids = set(po_places_ids + json_place_ids)

    places = list(UniquePlace.objects.annotate(
        pincode_count=Count("pincodes")
        ).filter(
            pincode_count__gt=1
        ).exclude(
            id__in = excluding_places_ids
        ).values_list("id", flat=True)
    )
    
    places_count = len(places)
    limit = int(places_count/3)

    place_ids_1 = places[:limit]
    place_ids_2 = places[limit:2*limit]
    place_ids_3 = places[2*limit:]

    run_india1.delay(place_ids_1)
    run_india2.delay(place_ids_2)
    run_india3.delay(place_ids_3)


@shared_task(queue="worker5_queue")
def save_locations():
    from .models import UniqueState, UniqueDistrict
    from django.utils.text import slugify

    state_names = UniqueState.objects.values_list("name", flat=True)
    correct_state_slugs = [slugify(name) for name in state_names]   
    states = UniqueState.objects.exclude(slug__in = correct_state_slugs).order_by("name")

    states_length = states.count()
    states_progress = 0

    logger.info("Updating state slugs . . .")

    for index, state in enumerate(states):
        current_state_progress = int((index+1)*100/states_length)
        if current_state_progress % 25 == 0 and current_state_progress != states_progress:
            states_progress = current_state_progress
            logger.info(f"Completed {states_progress}% of state slug updation.")
        
        state.slug = None
        state.save()

    logger.info("State slugs updated.")

    states = UniqueState.objects.all().order_by("name")

    for state in states:
        district_names = UniqueDistrict.objects.filter(state = state).values_list("name", flat=True)
        correct_district_slugs = [slugify(name) for name in district_names]
        districts = UniqueDistrict.objects.filter(state = state).exclude(slug__in = correct_district_slugs).order_by("name")

        districts_length = districts.count()
        districts_progress = 0

        logger.info(f"Updating district slugs of state: {state.name} . . .")

        for district_index, district in enumerate(districts):
            current_district_progress = int((district_index+1)*100/districts_length)
            if current_district_progress % 25 == 0 and current_district_progress != districts_progress:
                districts_progress = current_district_progress
                logger.info(f"Completed {districts_progress}% of {state.name} state's district slug updation.")

            district.slug = None
            district.save()

        logger.info(f"Updated district slugs of state: {state.name}.")

    logger.info(f"Updated all district slugs of India.")    

    for state in states:
        place_names = UniquePlace.objects.filter(state = state).values_list("name", flat=True)
        correct_place_slugs = [slugify(name) for name in place_names]
        places = UniquePlace.objects.filter(state = state).exclude(slug__in = correct_place_slugs).order_by("name")

        places_length = places.count()
        places_progress = 0

        logger.info(f"Updating place slugs of state: {state.name} . . .")

        for place_index, place in enumerate(places):
            current_place_progress = int((place_index+1)*100/places_length)
            if current_place_progress % 25 == 0 and current_place_progress != places_progress:
                places_progress = current_place_progress
                logger.info(f"Completed {places_progress}% of {state.name} state's place slug updation.")

            place.slug = None
            place.save()

        logger.info(f"Updated place slugs of state: {state.name}.")

    logger.info(f"Updated all place slugs of India.")    

    logger.info(f"Function Completed.")    



#########################################3
from .models import IndiaLocationData, PincodeAndCoordinate, UniquePlace

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


@shared_task(queue="worker5_queue")
def update_pincodes():
    import logging
    from .models import PlacePincode, PlaceCoordinate

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
                place_data = get_opencage_pincode_and_coordiante(item.json_data)
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

    logger.info(f"Completed")
