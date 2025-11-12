from django.shortcuts import render
import requests
import os
import pandas
import time
import sys
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.templatetags.static import static
from django.db import IntegrityError
from django.db.models import Q
import logging
from django.db import transaction

from .models import PostOffice, PoliceStation, Bank, Destination, Court

logger = logging.getLogger(__name__)

def row_generator(csv_data):
    for index, row in csv_data.iterrows():
        yield index, row

def import_postoffice_data():
    GREEN = "\033[92m"
    RESET = "\033[0m"

    # Corrected path string (remove the extra quotes)
    csv_data = pandas.read_csv(r"C:\Users\HP\Downloads\pincode.csv")
    length = len(csv_data)

    post_offices = []

    for index, row in csv_data.iterrows():
        time.sleep(0.001)

        circle_name = row["CircleName"] if pandas.notna(row["CircleName"]) else None
        region_name = row["RegionName"] if pandas.notna(row["RegionName"]) else None
        division_name = row["DivisionName"] if pandas.notna(row["DivisionName"]) else None
        office_name = row["OfficeName"] if pandas.notna(row["OfficeName"]) else None
        pincode = row["Pincode"] if pandas.notna(row["Pincode"]) else None
        office_type = row["OfficeType"] if pandas.notna(row["OfficeType"]) else None
        delivery = True if row["Delivery"] == "Delivery" else False
        district = row["District"] if pandas.notna(row["District"]) else None
        state_name = row["StateName"] if pandas.notna(row["StateName"]) else None
        latitude = row["Latitude"] if pandas.notna(row["Latitude"]) else None
        longitude = row["Longitude"] if pandas.notna(row["Longitude"]) else None
        
        post_offices.append(PostOffice(
            circle_name=circle_name,
            region_name=region_name,
            division_name=division_name,
            office_name=office_name,
            pincode=pincode,
            office_type=office_type,
            delivery=delivery,
            district=district,
            state_name=state_name,
            latitude=latitude,
            longitude=longitude
        ))

        # Progress bar display
        sys.stdout.write(
            f"{GREEN}\rExecuted {index + 1}/{length} rows - Completed {int((index + 1) / length * 100)}%{RESET}"
        )
        sys.stdout.flush()

    # Bulk create all the PostOffice instances at once
    PostOffice.objects.bulk_create(post_offices)

    print()  # To move the cursor to a new line after the progress bar

    
def import_police_stations():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:100];
    area["name"="India"]->.searchArea;
    (
    node["amenity"="police"](area.searchArea);
    way["amenity"="police"](area.searchArea);
    relation["amenity"="police"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status()

        data = response.json()
        police_stations = []

        for element in data.get('elements', []):
            if element.get("tags"):
                # Ensure essential fields are available
                name = element['tags'].get('name') or element['tags'].get('name:en')
                latitude = element.get('lat')
                longitude = element.get('lon')

                if not (name and latitude and longitude):
                    continue
                
                # Avoid duplicates
                if PoliceStation.objects.filter(
                    Q(latitude=latitude) & Q(longitude=longitude)
                ).exists():
                    continue

                # Create a new object
                police_stations.append(PoliceStation(
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    
                    name_gujarati = element['tags'].get('name:gu', None),
                    name_goan_konkani = element['tags'].get('name_goan_konkani', None),
                    name_santali = element['tags'].get('name:sat', None),
                    name_hindi = element['tags'].get('name:hi', None),
                    name_malayalam = element['tags'].get('name:ml', None),
                    name_punjabi = element['tags'].get('name:pa', None),
                    name_telugu = element['tags'].get('name:te', None),
                    name_kannada = element['tags'].get('name:kn', None),
                    name_bengali = element['tags'].get('name:bn', None),
                    name_marathi = element['tags'].get('name:mr', None),
                    name_tamil = element['tags'].get('name:ta', None),
                    name_odiya = element['tags'].get('name:or', None),
                    name_assamese = element['tags'].get('name:as', None),
                    name_kashmiri = element['tags'].get('name:ks', None),
                    name_urdu = element['tags'].get('name:ur', None),
                    name_maithili = element['tags'].get('name:mai', None),
                    name_sanskrit = element['tags'].get('name:sa', None),

                    pincode = element['tags'].get('postcode', None) or element['tags'].get('addr:postcode', None),
                    
                    street = element['tags'].get('addr:street', None),
                    city = element['tags'].get('addr:city', None),
                    district = element['tags'].get('addr:district', None),
                    state = element['tags'].get('addr:state', None),              

                    phone = element['tags'].get('phone', None),
                    website = element['tags'].get('website', None),
                ))

        # Bulk create objects
        PoliceStation.objects.bulk_create(police_stations)

        logger.info(f"Successfully imported {len(police_stations)} police stations into the database.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
    except ValueError:
        logger.error("Invalid JSON response received from Overpass API.")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")



def row_generator(csv_data):
    for index, row in csv_data.iterrows():
        yield index, row

def import_banks():
    GREEN = "\033[92m"
    RESET = "\033[0m"

    file = r"D:\Projects\BZ India\bzindia\static\w3\document\bank\bank.csv"
    csv_data = pandas.read_csv(file)

    banks = []  # List to hold Bank objects
    length = len(csv_data)

    for index, row in row_generator(csv_data):
        bank = Bank(
            name = row["BANK"],
            ifsc = row["IFSC"],
            branch = row["BRANCH"],
            center = row["CENTRE"],
            city = row["CITY"],
            district = row["DISTRICT"],
            state = row["STATE"],
            address = row["ADDRESS"],
            contact = row["CONTACT"],
            iso3166 = row["ISO3166"],
            micr = row["MICR"],
            swift = row["SWIFT"] if row["SWIFT"] and row["SWIFT"] != "nan" else None,
            imps = True if row["IMPS"] == "True" else False,
            rtgs = True if row["RTGS"] == "True" else False,
            neft = True if row["NEFT"] == "True" else False,
            upi = True if row["UPI"] == "True" else False
        )
        banks.append(bank)

        # Progress bar
        sys.stdout.write(
            f"{GREEN}\rProcessed {index + 1}/{length} rows - Completed {int((index + 1) / length * 100)}%{RESET}"
        )
        sys.stdout.flush()

    # Bulk creation
    Bank.objects.bulk_create(banks, ignore_conflicts=True)
    print("\nImport complete!")


def import_courts():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
        [out:json][timeout:100];
        area["name"="India"]->.searchArea;
        (
        node["amenity"="courthouse"](area.searchArea);
        way["amenity"="courthouse"](area.searchArea);
        relation["amenity"="courthouse"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
    """
    try:
        # Send the request to Overpass API
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        print(data)

        tags = []
        lis = set()
                                                            
        # # Iterate over the elements in the response
        for element in data.get('elements', []):
            if element.get("tags"):
                print("/n",element.get("tags"))        

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Overpass API: {e}")
    except ValueError:
        print("Invalid JSON response received from Overpass API.")
            

def import_attractions():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:100];
    area["name"="India"]->.searchArea;
    (
      node["tourism"="attraction"](area.searchArea);
      way["tourism"="attraction"](area.searchArea);
      relation["tourism"="attraction"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status()

        data = response.json()
        attractions = []

        for element in data.get('elements', []):
            if element.get("tags"):
                # Ensure essential fields are available
                name = element['tags'].get('name') or element['tags'].get('name:en')
                alternative_name = element['tags'].get('alt_name')
                latitude = element.get('lat')
                longitude = element.get('lon')

                # if not (name or alternative_name) and not (latitude and longitude): # 09/05/2025
                #     continue
                
                # Avoid duplicates
                if Destination.objects.filter(
                    latitude=latitude,
                    longitude=longitude
                ).exclude(
                    Q(latitude__isnull=True) | Q(longitude__isnull=True)
                ).exists():
                    continue

                # Create a new object
                attractions.append(Destination(
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    
                    old_name = element['tags'].get('old_name', None),

                    alternative_name = element['tags'].get('alt_name', None),

                    alternative_name_hindi = element['tags'].get('alt_name:hi', None),
                    alternative_name_bengali = element['tags'].get('alt_name:bn', None),
                    alternative_name_marathi = element['tags'].get('alt_name:mr', None),
                    alternative_name_kannada = element['tags'].get('alt_name:kn', None),
                    alternative_name_maithili = element['tags'].get('alt_name:mai', None),
                    alternative_name_malayalam = element['tags'].get('alt_name:ml', None),
                    alternative_name_tamil = element['tags'].get('alt_name:ta', None),
                    
                    name_gujarati = element['tags'].get('name:gu', None),
                    name_goan_konkani = element['tags'].get('name_goan_konkani', None),
                    name_santali = element['tags'].get('name:sat', None),
                    name_hindi = element['tags'].get('name:hi', None),
                    name_malayalam = element['tags'].get('name:ml', None),
                    name_punjabi = element['tags'].get('name:pa', None),
                    name_telugu = element['tags'].get('name:te', None),
                    name_kannada = element['tags'].get('name:kn', None),
                    name_bengali = element['tags'].get('name:bn', None),
                    name_marathi = element['tags'].get('name:mr', None),
                    name_tamil = element['tags'].get('name:ta', None),
                    name_odiya = element['tags'].get('name:or', None),
                    name_assamese = element['tags'].get('name:as', None),
                    name_kashmiri = element['tags'].get('name:ks', None),
                    name_urdu = element['tags'].get('name:ur', None),
                    name_maithili = element['tags'].get('name:mai', None),
                    name_sanskrit = element['tags'].get('name:sa', None),

                    historic_type = element['tags'].get('historic', None),

                    wheelchair_accessible = element['tags'].get('wheelchair', None),

                    sport_type = element['tags'].get('sport', None),

                    leisure_activity = element['tags'].get('leisure', None),

                    denomination = element['tags'].get('denomination', None),
                    religion = element['tags'].get('religion', None),

                    house_number = element['tags'].get('house_number', None),
                    pincode = element['tags'].get('postcode', None) or element['tags'].get('addr:postcode', None),
                    
                    street = element['tags'].get('addr:street', None),
                    place = element['tags'].get('addr:place', None),
                    city = element['tags'].get('addr:city', None),
                    district = element['tags'].get('addr:district', None),
                    state = element['tags'].get('addr:state', None),
                    place_type = element['tags'].get('place', None),
                    building_type = element['tags'].get('amenity', None),
                    building_category = element['tags'].get('building', None),
                    elevation = element['tags'].get('ele', None),
                    geography_type = element['tags'].get('natural', None),
                    man_made_contribution = element['tags'].get('man_made', None),
                    memmorial_type = element['tags'].get('memorial', None),

                    building_height = element['tags'].get('height', None),

                    waterway_type = element['tags'].get('waterway', None),
                    waterbody_type = element['tags'].get('water', None),
                    castle_type = element['tags'].get('castle', None),
                    attraction = element['tags'].get('attraction', None),

                    operated_by = element['tags'].get('operated_by', None),
                    opening_hours = element['tags'].get('opening_hours', None),
                    access_type = element['tags'].get('access', None),

                    started_date = element['tags'].get('start_date', None),

                    shops_available = element['tags'].get('shop', None),

                    description = element['tags'].get('description', None),
                    note = element['tags'].get('note', None),

                    phone = element['tags'].get('phone', None),
                    email = element['tags'].get('email', None),

                    website = element['tags'].get('website', None),
                ))

        # Bulk create objects
        Destination.objects.bulk_create(attractions)

        logger.info(f"Successfully imported {len(attractions)} attractions into the database.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
    except ValueError:
        logger.error("Invalid JSON response received from Overpass API.")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")


def import_courts_data():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:100];
    area["name"="India"]->.searchArea;
    (
    node["amenity"="courthouse"](area.searchArea);
    way["amenity"="courthouse"](area.searchArea);
    relation["amenity"="courthouse"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status()

        data = response.json()
        courts = []

        for element in data.get('elements', []):
            if element.get("tags"):
                # Ensure essential fields are available
                name = element['tags'].get('name') or element['tags'].get('name:en')
                latitude = element.get('lat')
                longitude = element.get('lon')

                if not (name and latitude and longitude):
                    continue
                
                # Avoid duplicates
                if Court.objects.filter(
                    Q(latitude=latitude) & Q(longitude=longitude)
                ).exists():
                    continue

                # Create a new object
                courts.append(Court(
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    
                    old_name = element['tags'].get('old_name', None),
                    designation = element['tags'].get('designation', None),                    
                    
                    name_gujarati = element['tags'].get('name:gu', None),
                    name_goan_konkani = element['tags'].get('name_goan_konkani', None),
                    name_santali = element['tags'].get('name:sat', None),
                    name_hindi = element['tags'].get('name:hi', None),
                    name_malayalam = element['tags'].get('name:ml', None),
                    name_punjabi = element['tags'].get('name:pa', None),
                    name_telugu = element['tags'].get('name:te', None),
                    name_kannada = element['tags'].get('name:kn', None),
                    name_bengali = element['tags'].get('name:bn', None),
                    name_marathi = element['tags'].get('name:mr', None),
                    name_tamil = element['tags'].get('name:ta', None),
                    name_odiya = element['tags'].get('name:or', None),
                    name_assamese = element['tags'].get('name:as', None),
                    name_kashmiri = element['tags'].get('name:ks', None),
                    name_urdu = element['tags'].get('name:ur', None),
                    name_maithili = element['tags'].get('name:mai', None),
                    name_sanskrit = element['tags'].get('name:sa', None),

                    pincode = element['tags'].get('postcode', None) or element['tags'].get('addr:postcode', None),
                    
                    street = element['tags'].get('addr:street', None),
                    city = element['tags'].get('addr:city', None),
                    district = element['tags'].get('addr:district', None),
                    state = element['tags'].get('addr:state', None),              

                    opening_hours = element['tags'].get('opening_hours', None),

                    phone = element['tags'].get('phone', None),
                    website = element['tags'].get('website', None),
                ))

        # Bulk create objects
        Court.objects.bulk_create(courts)

        logger.info(f"Successfully imported {len(courts)} courts into the database.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
    except ValueError:
        logger.error("Invalid JSON response received from Overpass API.")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")


def fetch_destination_locations(batch_size=100, buffer_size=10):
    api_key = os.getenv("OPENCAGE_API_KEY_1")
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    destinations_qs = Destination.objects.filter(
        Q(place__isnull=True) |
        Q(district__isnull=True) |
        Q(state__isnull=True) |
        Q(pincode__isnull=True)
    ).exclude(
        latitude__isnull=True, longitude__isnull=True
    ).order_by('id')  # Always order when paginating

    total = destinations_qs.count()
    logger.info(f"Found {total} destinations to update")

    paginator = Paginator(destinations_qs, batch_size)
    counting = 0

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        updating_destinations = []

        logger.info(f"Processing batch {page_number}/{paginator.num_pages} (Batch size: {batch_size})")

        for destination in page.object_list:
            latitude = destination.latitude
            longitude = destination.longitude

            try:
                response = requests.get(
                    base_url,
                    params={'q': f'{latitude}+{longitude}', 'key': api_key},
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()

                if data.get("results"):
                    components = data["results"][0].get("components", {})
                    if components.get("country") == "India":

                        place = components.get("hamlet") \
                                or components.get("village") \
                                or components.get("neighbourhood") \
                                or components.get("suburb") \
                                or components.get("town") \
                                or components.get("city_district") \
                                or components.get("municipality") \
                                or components.get("city") \
                                or components.get("county")

                        state = components.get("state")
                        district = components.get("state_district")
                        pincode = components.get("postcode")

                        if not district and components.get("suburb") and components.get("city"):
                            district = components.get("city")

                        if any([place, district, state, pincode]):
                            destination.place = place or destination.place
                            destination.district = district or destination.district
                            destination.state = state or destination.state
                            destination.pincode = pincode or destination.pincode

                            updating_destinations.append(destination)
                            counting += 1

                            percentage = (counting / total) * 100 if total else 0
                            logger.info(f"Progress: {percentage:.2f}%")

                            # Flush buffer every `buffer_size` records
                            if len(updating_destinations) >= buffer_size:
                                with transaction.atomic():
                                    Destination.objects.bulk_update(
                                        updating_destinations, ["place", "district", "state", "pincode"]
                                    )
                                logger.info(f"Buffered update: {buffer_size} destinations updated")
                                updating_destinations.clear()  # reset buffer

                time.sleep(0.25)  # Respect API rate limit

            except requests.exceptions.RequestException as e:
                logger.error(f"API request error for ({latitude}, {longitude}): {e}")
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit exceeded. Sleeping for {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    logger.warning("Retrying after 5 seconds...")
                    time.sleep(5)
                continue

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(5)
                continue

        # Flush remaining buffered updates after batch
        if updating_destinations:
            with transaction.atomic():
                Destination.objects.bulk_update(
                    updating_destinations, ["place", "district", "state", "pincode"]
                )
            logger.info(f"Final buffered update: {len(updating_destinations)} destinations updated for batch {page_number}")
            updating_destinations.clear()

    logger.info("Location fetching completed for all destinations!")

def fetch_police_locations(batch_size=100, buffer_size=10):
    api_key = os.getenv("OPENCAGE_API_KEY_2")
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    police_stations_qs = PoliceStation.objects.filter(
        Q(city__isnull=True) |
        Q(district__isnull=True) |
        Q(state__isnull=True) |
        Q(pincode__isnull=True)
    ).exclude(
        latitude__isnull=True, longitude__isnull=True
    ).order_by('id')  # Always order when paginating

    total = police_stations_qs.count()
    logger.info(f"Found {total} police stations to update")

    paginator = Paginator(police_stations_qs, batch_size)
    counting = 0

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        updating_police_stations = []

        logger.info(f"Processing batch {page_number}/{paginator.num_pages} (Batch size: {batch_size})")

        for police_station in page.object_list:
            latitude = police_station.latitude
            longitude = police_station.longitude

            try:
                response = requests.get(
                    base_url,
                    params={'q': f'{latitude}+{longitude}', 'key': api_key},
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()

                if data.get("results"):
                    components = data["results"][0].get("components", {})
                    if components.get("country") == "India":
                        city = components.get("hamlet") \
                                or components.get("village") \
                                or components.get("neighbourhood") \
                                or components.get("suburb") \
                                or components.get("town") \
                                or components.get("city_district") \
                                or components.get("municipality") \
                                or components.get("city") \
                                or components.get("county")
                        state = components.get("state")
                        district = components.get("state_district")
                        pincode = components.get("postcode")

                        if not district and components.get("suburb") and components.get("city"):
                            district = components.get("city")

                        if any([city, district, state, pincode]):
                            police_station.city = city or police_station.city
                            police_station.district = district or police_station.district
                            police_station.state = state or police_station.state
                            police_station.pincode = pincode or police_station.pincode

                            updating_police_stations.append(police_station)
                            counting += 1

                            percentage = (counting / total) * 100 if total else 0
                            logger.info(f"Progress: {percentage:.2f}%")

                            # Flush buffer every `buffer_size` records
                            if len(updating_police_stations) >= buffer_size:
                                with transaction.atomic():
                                    PoliceStation.objects.bulk_update(
                                        updating_police_stations, ["city", "district", "state", "pincode"]
                                    )
                                logger.info(f"Buffered update: {buffer_size} police stations updated")
                                updating_police_stations.clear()  # reset buffer

                time.sleep(0.25)  # Respect API rate limit

            except requests.exceptions.RequestException as e:
                logger.error(f"API request error for ({latitude}, {longitude}): {e}")
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit exceeded. Sleeping for {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    logger.warning("Retrying after 5 seconds...")
                    time.sleep(5)
                continue

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(5)
                continue

        # Flush remaining buffered updates after batch
        if updating_police_stations:
            with transaction.atomic():
                PoliceStation.objects.bulk_update(
                    updating_police_stations, ["city", "district", "state", "pincode"]
                )
            logger.info(f"Final buffered update: {len(updating_police_stations)} police stations updated for batch {page_number}")
            updating_police_stations.clear()

    logger.info("Location fetching completed for all police stations!")

def fetch_court_locations(batch_size=100, buffer_size=10):
    api_key = os.getenv("OPENCAGE_API_KEY_3")
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    courts_qs = Court.objects.filter(
        Q(city__isnull=True) |
        Q(district__isnull=True) |
        Q(state__isnull=True) |
        Q(pincode__isnull=True)
    ).exclude(
        latitude__isnull=True, longitude__isnull=True
    ).order_by('id')  # Always order when paginating

    total = courts_qs.count()
    logger.info(f"Found {total} courts to update")

    paginator = Paginator(courts_qs, batch_size)
    counting = 0

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        updating_courts = []

        logger.info(f"Processing batch {page_number}/{paginator.num_pages} (Batch size: {batch_size})")

        for court in page.object_list:
            latitude = court.latitude
            longitude = court.longitude

            try:
                response = requests.get(
                    base_url,
                    params={'q': f'{latitude}+{longitude}', 'key': api_key},
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()

                if data.get("results"):
                    components = data["results"][0].get("components", {})
                    if components.get("country") == "India":

                        city = components.get("hamlet") \
                                or components.get("village") \
                                or components.get("neighbourhood") \
                                or components.get("suburb") \
                                or components.get("town") \
                                or components.get("city_district") \
                                or components.get("municipality") \
                                or components.get("city") \
                                or components.get("county")

                        state = components.get("state")
                        district = components.get("state_district")
                        pincode = components.get("postcode")

                        if not district and components.get("suburb") and components.get("city"):
                            district = components.get("city")

                        if any([city, district, state, pincode]):
                            court.city = city or court.city
                            court.district = district or court.district
                            court.state = state or court.state
                            court.pincode = pincode or court.pincode

                            updating_courts.append(court)
                            counting += 1

                            percentage = (counting / total) * 100 if total else 0
                            logger.info(f"Progress: {percentage:.2f}%")

                            # Flush buffer every `buffer_size` records
                            if len(updating_courts) >= buffer_size:
                                with transaction.atomic():
                                    Court.objects.bulk_update(
                                        updating_courts, ["city", "district", "state", "pincode"]
                                    )
                                logger.info(f"Buffered update: {buffer_size} courts updated")
                                updating_courts.clear()  # reset buffer

                time.sleep(0.25)  # Respect API rate limit

            except requests.exceptions.RequestException as e:
                logger.error(f"API request error for ({latitude}, {longitude}): {e}")
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit exceeded. Sleeping for {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    logger.warning("Retrying after 5 seconds...")
                    time.sleep(5)
                continue

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(5)
                continue

        # Flush remaining buffered updates after batch
        if updating_courts:
            with transaction.atomic():
                Court.objects.bulk_update(
                    updating_courts, ["city", "district", "state", "pincode"]
                )
            logger.info(f"Final buffered update: {len(updating_courts)} courts updated for batch {page_number}")
            updating_courts.clear()

    logger.info("Location fetching completed for all courts!")

import pandas as pd

def clean_string(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value if value and value.lower() != "nan" else None

def clean_number(value):
    try:
        if not value or pd.isna(value):
            return None
        number = str(value).split(',')[0].replace("+91", "").replace("'", "").strip()
        return int(float(number))
    except Exception:
        return None

# import csv
# from django.db import transaction
# from django.utils.text import slugify
# from .models import CscCenter
# from decimal import Decimal, InvalidOperation

# def import_csc_centers():
#     """
#     Import CSC Center data from a CSV file with proper type cleaning:
#     - Converts empty/NaN fields to None or ""
#     - Converts scientific notation (E+) to proper strings/numbers
#     - Uses bulk_create for high performance
#     """
#     csv_path = r"D:\Project Materials\BZ India\csc-centers.csv"

#     def clean_value(value: str, to_str=False):
#         """
#         Clean and normalize cell values:
#         - Converts NaN/nan/None to None
#         - Strips whitespace
#         - Converts numbers in scientific notation to normal strings
#         """
#         if value is None:
#             return None

#         value = str(value).strip()

#         if value == "" or value.lower() == "nan":
#             return None

#         # Handle scientific notation like 1.23E+11
#         try:
#             if "e" in value.lower():
#                 num = Decimal(value)
#                 value = format(num, "f").rstrip("0").rstrip(".")
#         except InvalidOperation:
#             pass  # not a number — keep as string

#         # Return string or None depending on field type
#         return value if to_str else value

#     try:
#         with open(csv_path, newline="", encoding="utf-8") as csvfile:
#             reader = list(csv.DictReader(csvfile))
#             total_rows = len(reader)

#             if total_rows == 0:
#                 print("CSV file is empty.")
#                 return

#             print(f"Starting import of {total_rows} CSC centers...")

#             new_centers = []

#             for index, row in enumerate(reader, start=1):
#                 get = lambda key: clean_value(row.get(key))

#                 csc_center = CscCenter(
#                     csc_id=get("id"),
#                     title=get("title"),
#                     name=get("name"),
#                     slug=slugify(get("slug") or get("name") or ""),

#                     state_name=get("state"),
#                     district_name=get("district"),
#                     place_name=get("block"),

#                     location=get("address"),
#                     pincode=get("pincode"),
#                     street=get("place"),

#                     owner=get("owner"),
#                     email=get("email"),

#                     contact_number=get("phone") if get("phone") and len(get("phone")) < 25 else None,
#                     mobile_number=get("phone2") if get("phone2") and len(get("phone2")) < 25 else None,
#                     whatsapp_number=get("whatsapp") if get("whatsapp") and len(get("whatsapp")) < 25 else None,

#                     all_registrations=get("services"),

#                     latitude=get("latitude") if get("latitude") and len(get("latitude")) < 10 else None,
#                     longitude=get("longitude") if get("longitude") and len(get("longitude")) < 10 else None,
#                 )

#                 new_centers.append(csc_center)

#                 # Print progress every 100 rows to avoid console lag
#                 if index % 100 == 0 or index == total_rows:
#                     percent_done = (index / total_rows) * 100
#                     print(f"\rProgress: {percent_done:.2f}%", end="")

#             with transaction.atomic():
#                 CscCenter.objects.bulk_create(new_centers, batch_size=1000)

#             print("\n✅ Import completed successfully!")

#     except Exception as e:
#         print(f"\n❌ Error during import: {e}")


# def get_decimal_coordinates():
#     from .models import CscCenter

#     csc_centers = CscCenter.objects.filter(
#         latitude__isnull=False,
#         longitude__isnull=False
#         ).filter(
#             Q(decimal_latitude__isnull=True) | Q(decimal_longitude__isnull=True)
#         ).iterator()

#     updating_csc_centers = []

#     for center in csc_centers:
#         try:
#             lat_str = str(center.latitude).strip()
#             lon_str = str(center.longitude).strip()

#             if not lat_str or not lon_str or lat_str.lower() == "nan" or lon_str.lower() == "nan":
#                 continue

#             decimal_latitude = float(lat_str)
#             decimal_longitude = float(lon_str)

#             center.decimal_latitude = decimal_latitude
#             center.decimal_longitude = decimal_longitude
            
#             updating_csc_centers.append(center)
#         except (ValueError, TypeError):
#             continue

#     CscCenter.objects.bulk_update(updating_csc_centers, ["decimal_latitude", "decimal_longitude"])

