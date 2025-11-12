from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
import requests, os, logging

from service.models import Service
from company.models import Company, CompanyType
from directory.models import TouristAttraction
from locations.models import Place
from locations.models import IndianLocation, SuburbLocationData, IndiaLocationData

import hashlib



logger = logging.getLogger(__name__)

class BaseView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["company_types"] = CompanyType.objects.all().order_by("name")

        context["attractions"] = TouristAttraction.objects.filter(
                Q(name__isnull=False) & (
                    Q(historic_type__isnull=False) | 
                    Q(waterway_type__isnull=False) | 
                    Q(waterbody_type__isnull=False)
                )
                ).exclude(
                    Q(historic_type="yes") & 
                    Q(waterway_type="yes") & 
                    Q(waterbody_type="yes")
                ).order_by("?")[:12]     

        return context
    

class GetLocalPlacesView(View):
    def get(self, request, *args, **kwargs):
        pincode = self.kwargs.get("pincode")

        places = Place.objects.filter(pincode = pincode).distinct().order_by("name")
        list_places = list(places.values("name", "slug"))

        data = {
            "success": True, "places": list_places, "pincode": pincode
        }

        first_location = places.first() if places else None

        if first_location:
            place = first_location.name
            district = first_location.district.name
            state = first_location.state.name
            latitude = first_location.latitude
            longitude = first_location.longitude

            data.update({
                "place": place,
                "district": district,
                "state": state
            })

            services = Service.objects.all().order_by("?")

            service_schema = {
                "@context": "http://schema.org",
                "@type": "ItemList",
                "itemListElement": [
                    {
                    "@type": "ListItem",
                    "position": f"{index + 1}",
                    "item": {
                        "@type": "Service",
                        "provider": {
                        "@type": "Organization",
                        "name": f"{service.company.name}",
                        "url": f"https://www.bzindia.in/company/{service.company.slug}",
                        "logo": f"https://www.bzindia.in{service.company.logo.url if service.company.logo else '/#'}",
                        "address": {
                            "@type": "PostalAddress",
                            "streetAddress": f"{place}",
                            "addressLocality": f"{district}",
                            "addressRegion": f"{state}",
                            "postalCode": f"{pincode}",
                            "addressCountry": "IN"
                        },
                        "location": {
                            "@type": "Place",
                            "geo": {
                            "@type": "GeoCoordinates",
                            "latitude": f"{latitude}",
                            "longitude": f"{longitude}"
                            }
                        }
                        },
                        "name": f"{service.name}",
                        "description": f"{service.description}",
                        "image": f"https://www.bzindia.in/{service.image.url if service.image else '#'}",
                        "url": f"https://www.bzindia.in/service/{service.slug}"
                    }
                    } for index, service in enumerate(services)
                ]
            }

            data["service_schema"] = service_schema

        return JsonResponse(data)


class GetPincodeView(View):
    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get("x-requested-with") != "XMLHttpRequest":
                return JsonResponse({"failed": True, "message": "Method Not Allowed"}, status=403)

            latitude = self.kwargs.get("latitude")
            longitude = self.kwargs.get("longitude")

            opencage_api = os.getenv('OPENCAGE_API_KEY_1') 

            if not latitude or not longitude or not opencage_api:
                return JsonResponse({"failed": True, "message": "Bad Request"}, status=400)

            url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={opencage_api}'

            response = requests.get(url)
            data = response.json()

            if not data['results'] or not data['results'][0]['components']['postcode']:
                return JsonResponse({"failed": True, "message": "Not Found"}, status=404)

            pincode = data['results'][0]['components']['postcode']

            return redirect(reverse_lazy('base:get_places', kwargs = {'pincode': pincode}))
        
        except Exception as e:
            logger.exception(f"Error in get function of GetPincodeView of base app: {e}")
            return JsonResponse({"failed": True, "message": "An unexpected error occured"}, status=500)


from product.models import (
    Product, Category as ProductCategory, SubCategory as ProductSubCategory,
    ProductDetailPage, MultiPage as ProductMultipage
    )
from service.models import (
    Service, Category as ServiceCategory, SubCategory as ServiceSubCategory,
    ServiceDetail, MultiPage as ServiceMultipage
    )
from registration.models import (
    Registration, RegistrationType, RegistrationSubType,
    RegistrationDetailPage, MultiPage as RegistrationMultipage
    )
from educational.models import (
    Course, Program, Specialization, CourseDetail, MultiPage as CourseMultipage
    )
from django.db import transaction
import sys

class UpdateSlugs:    
    def __init__(self):  
        sys.stdout.write("\nFunction Initiated!\n")
        
        try:
            self.update_products()
            print()
            self.update_services()
            print()
            self.update_registrations()
            print()
            self.update_courses()
            print()
        
        except Exception as e:
            logger.exception(f"Error Occured: {e}")
            sys.stdout.write("Error! Updation not completed!\n")

        sys.stdout.write("\nAll Done. Updation Completed!\n")


    def update_products(self):
        items = Product.objects.all()
        total_items = items.count()
        print()

        with transaction.atomic():
            items.update(slug = None)
            for item_index, item in enumerate(Product.objects.iterator()):
                item.save()
                print(f"\rProduct Slugs Updated: {int(((item_index + 1)/total_items)*100)}%", end="")        


        categories = ProductCategory.objects.all()
        total_categories = categories.count()
        print()

        with transaction.atomic():
            categories.update(slug = None)
            for category_index, category in enumerate(ProductCategory.objects.iterator()):                
                category.save()
                print(f"\rProduct Category Slugs Updated: {int(((category_index + 1)/total_categories)*100)}%", end="")        

        sub_categories = ProductSubCategory.objects.all()
        total_sub_categories = sub_categories.count()
        print()

        with transaction.atomic():
            sub_categories.update(slug = None)
            for sub_category_index, sub_category in enumerate(ProductSubCategory.objects.iterator()):                
                sub_category.save()
                print(f"\rProduct Sub Category Slugs Updated: {int(((sub_category_index + 1)/total_sub_categories)*100)}%", end="")        

        detail_pages = ProductDetailPage.objects.all()
        total_detail_pages = detail_pages.count()
        print()
        
        with transaction.atomic():
            detail_pages.update(slug = None)
            for detail_page_index, detail_page in enumerate(ProductDetailPage.objects.iterator()):                
                detail_page.save()
                print(f"\rProduct Detail Page Slugs Updated: {int(((detail_page_index + 1)/total_detail_pages)*100)}%", end="")        

        multipages = ProductMultipage.objects.all()
        total_multipages = multipages.count()
        print()
        
        with transaction.atomic():
            multipages.update(slug = None)
            for multipage_index, multipage in enumerate(ProductMultipage.objects.iterator()):                
                multipage.save()
                print(f"\rProduct Multipage Slugs Updated: {int(((multipage_index + 1)/total_multipages)*100)}%", end="")    

    def update_services(self):
        items = Service.objects.all()
        total_items = items.count()
        print()
        
        with transaction.atomic():
            items.update(slug = None)
            for item_index, item in enumerate(Service.objects.iterator()):                
                item.save()
                print(f"\rService Slugs Updated: {int(((item_index + 1)/total_items)*100)}%", end="")        

        categories = ServiceCategory.objects.all()
        total_categories = categories.count()
        print()

        with transaction.atomic():
            categories.update(slug = None)
            for category_index, category in enumerate(ServiceCategory.objects.iterator()):
                category.save()
                print(f"\rService Category Slugs Updated: {int(((category_index + 1)/total_categories)*100)}%", end="")        

        sub_categories = ServiceSubCategory.objects.all()
        total_sub_categories = sub_categories.count()
        print()
        
        with transaction.atomic():
            sub_categories.update(slug = None)
            for sub_category_index, sub_category in enumerate(ServiceSubCategory.objects.iterator()):                
                sub_category.save()
                print(f"\rService Sub Category Slugs Updated: {int(((sub_category_index + 1)/total_sub_categories)*100)}%", end="")        

        detail_pages = ServiceDetail.objects.all()
        total_detail_pages = detail_pages.count()
        print()
        
        with transaction.atomic():
            detail_pages.update(slug = None)
            for detail_page_index, detail_page in enumerate(ServiceDetail.objects.iterator()):                
                detail_page.save()
                print(f"\rService Detail Page Slugs Updated: {int(((detail_page_index + 1)/total_detail_pages)*100)}%", end="")        

        multipages = ServiceMultipage.objects.all()
        total_multipages = multipages.count()
        print()
        
        with transaction.atomic():
            multipages.update(slug = None)
            for multipage_index, multipage in enumerate(ServiceMultipage.objects.iterator()):                
                multipage.save()
                print(f"\rService Multipage Slugs Updated: {int(((multipage_index + 1)/total_multipages)*100)}%", end="")    
    
    def update_registrations(self):
        items = Registration.objects.all()
        total_items = items.count()
        print()
        
        with transaction.atomic():
            items.update(slug = None)
            for item_index, item in enumerate(Registration.objects.iterator()):                
                item.save()
                print(f"\rRegistration Slugs Updated: {int(((item_index + 1)/total_items)*100)}%", end="")        

        types = RegistrationType.objects.all()
        total_types = types.count()
        print()
        
        with transaction.atomic():
            types.update(slug = None)
            for registration_type_index, registration_type in enumerate(RegistrationType.objects.iterator()):                
                registration_type.save()            
                print(f"\rRegistration Type Slugs Updated: {int(((registration_type_index + 1)/total_types)*100)}%", end="")        

        sub_types = RegistrationSubType.objects.all()
        total_sub_types = sub_types.count()
        print()
        
        with transaction.atomic():
            sub_types.update(slug = None)
            for sub_type_index, sub_type in enumerate(RegistrationSubType.objects.iterator()):                
                sub_type.save()
                print(f"\rRegistration Sub Type Slugs Updated: {int(((sub_type_index + 1)/total_sub_types)*100)}%", end="")        

        detail_pages = RegistrationDetailPage.objects.all()
        total_detail_pages = detail_pages.count()
        print()
        
        with transaction.atomic():
            detail_pages.update(slug = None)
            for detail_page_index, detail_page in enumerate(RegistrationDetailPage.objects.iterator()):                
                detail_page.save()
                print(f"\rRegistration Detail Page Slugs Updated: {int(((detail_page_index + 1)/total_detail_pages)*100)}%", end="")        

        multipages = RegistrationMultipage.objects.all()
        total_multipages = multipages.count()
        print()
        
        with transaction.atomic():
            multipages.update(slug = None)
            for multipage_index, multipage in enumerate(RegistrationMultipage.objects.iterator()):                
                multipage.save()
                print(f"\rRegistration Multipage Slugs Updated: {int(((multipage_index + 1)/total_multipages)*100)}%", end="")    

    def update_courses(self):
        items = Course.objects.all()
        total_items = items.count()
        print()
        
        with transaction.atomic():
            items.update(slug = None)
            for item_index, item in enumerate(Course.objects.iterator()):                
                item.save()
                print(f"\rCourse Slugs Updated: {int(((item_index + 1)/total_items)*100)}%", end="")        

        programs = Program.objects.all()
        total_programs = programs.count()
        print()
        
        with transaction.atomic():
            programs.update(slug = None)
            for program_index, program in enumerate(Program.objects.iterator()):                
                program.save()
                print(f"\rProgram Slugs Updated: {int(((program_index + 1)/total_programs)*100)}%", end="")        

        specializations = Specialization.objects.all()
        total_specializations = specializations.count()
        print()
        
        with transaction.atomic():
            specializations.update(slug = None)
            for specialization_index, specialization in enumerate(Specialization.objects.iterator()):                
                specialization.save()
                print(f"\rSpecialization Slugs Updated: {int(((specialization_index + 1)/total_specializations)*100)}%", end="")        

        detail_pages = CourseDetail.objects.all()
        total_detail_pages = detail_pages.count()
        print()
        
        with transaction.atomic():
            detail_pages.update(slug = None)
            for detail_page_index, detail_page in enumerate(CourseDetail.objects.iterator()):                
                detail_page.save()
                print(f"\rCourse Detail Page Slugs Updated: {int(((detail_page_index + 1)/total_detail_pages)*100)}%", end="")        

        multipages = CourseMultipage.objects.all()
        total_multipages = multipages.count()
        print()
        
        with transaction.atomic():
            multipages.update(slug = None)
            for multipage_index, multipage in enumerate(CourseMultipage.objects.iterator()):                
                multipage.save()
                print(f"\rCourse Multipage Slugs Updated: {int(((multipage_index + 1)/total_multipages)*100)}%", end="")    

                
def update_slugs():
    _ = UpdateSlugs()


# def check_location(offset=0, limit=9000):
#     from locations.models import IndiaLocationData

#     matches = []

#     queryset = IndiaLocationData.objects.filter(
#         requested_latitude__lt=22.0,
#         requested_latitude__gt=15.6,
#         requested_longitude__gt=72.6,
#         requested_longitude__lt=80.9,
#     ).order_by("id")

#     for idx, item in enumerate(queryset.iterator(chunk_size=500)):
#         if idx < offset:
#             continue
#         if idx >= offset + limit:
#             break

#         json_data = getattr(item, "json_data", {})
#         results = json_data.get("results", [])
#         if not results:
#             continue

#         components = results[0].get("components", {})
#         district = components.get("state_district", "")
#         state = components.get("state", "")
#         suburb = components.get("suburb", "")

#         if suburb == "Colaba":
#             print(f"{idx}: Suburb={suburb}, district={district}, state={state}")
#             print(results[0])

#         if "mumbai" in district.lower():
#             matches.append({
#                 "address": getattr(item, "address", None),
#                 "district": district,
#                 "state": state,
#                 "formatted": results[0].get("formatted"),
#                 "latitude": results[0]["geometry"]["lat"],
#                 "longitude": results[0]["geometry"]["lng"],
#             })

#     print(f"Found {len(matches)} matches in this batch")

#     return {
#         "total_matches": len(matches),
#         "results": matches
#     }


def populate_indian_locations(batch_size=5000):
    
    queryset = IndiaLocationData.objects.filter(json_data__isnull=False).order_by("id")
    total = queryset.count()
    print(f"Processing {total} records...")

    for start in range(0, total, batch_size):
        batch = list(queryset[start:start + batch_size])
        if not batch:
            continue

        # Preload existing IndianLocation by source_id
        existing_ids = set(IndianLocation.objects.filter(
            source_id__in=[item.id for item in batch]
        ).values_list('source_id', flat=True))

        creates, updates = [], []
        data_updates = []

        for item in batch:
            json_data = item.json_data
            if not json_data:
                continue

            # Compute JSON hash
            json_string = str(json_data).encode('utf-8')
            json_hash = hashlib.sha256(json_string).hexdigest()

            # Skip if already processed same JSON
            if item.json_hash == json_hash:
                continue

            results = json_data.get("results", [])
            if not results:
                continue

            components = results[0].get("components", {})
            geometry = results[0].get("geometry", {})

            # Prepare IndianLocation data
            loc_data = {
                "source_id": item.id,
                "country": components.get("country"),
                "country_code": components.get("country_code"),
                "state": components.get("state"),
                "state_code": components.get("state_code"),
                "district": components.get("state_district"),
                "county": components.get("county"),
                "city": components.get("city"),
                "town": components.get("town"),
                "village": components.get("village"),
                "suburb": components.get("suburb"),
                "city_district": components.get("city_district"),
                "postcode": components.get("postcode"),
                "place_type": components.get("_type"),
                "latitude": geometry.get("lat"),
                "longitude": geometry.get("lng"),
                "iso_codes": {
                    "alpha2": components.get("ISO_3166-1_alpha-2"),
                    "alpha3": components.get("ISO_3166-1_alpha-3"),
                    "iso_2": components.get("ISO_3166-2"),
                },
                "formatted": results[0].get("formatted"),
                "confidence": results[0].get("confidence"),
                "json_hash": json_hash,
            }

            if item.id in existing_ids:
                # Existing row → update
                loc = IndianLocation(source_id=item.id, **loc_data)
                updates.append(loc)
            else:
                # New row → create
                loc = IndianLocation(**loc_data)
                creates.append(loc)

            # Schedule IndiaLocationData hash update
            item.json_hash = json_hash
            data_updates.append(item)

        with transaction.atomic():
            if creates:
                IndianLocation.objects.bulk_create(creates, batch_size=batch_size)
            if updates:
                IndianLocation.objects.bulk_update(
                    updates,
                    [
                        "country", "country_code", "state", "state_code", "district",
                        "city", "town", "village", "suburb", "city_district", "postcode",
                        "place_type", "latitude", "longitude",
                        "iso_codes", "formatted", "confidence", "json_hash",
                    ],
                    batch_size=batch_size
                )
            if data_updates:
                IndiaLocationData.objects.bulk_update(data_updates, ["json_hash"])

        print(f"✅ Processed {min(start + batch_size, total)} / {total} records")


def get_suburb_locations():
    import time

    logger = logging.getLogger(__name__)

    base_url = 'https://api.opencagedata.com/geocode/v1/json'
    api_key = os.getenv('OPENCAGE_API_KEY_1')

    if not api_key:
        logger.error("Missing OPENCAGE_API_KEY_1 in environment variables.")
        return

    suburb_list = list(
        IndianLocation.objects.filter(
            suburb__isnull=False,
            district__isnull=True
        ).exclude(suburb__exact="").values_list("suburb", flat=True).distinct()
    )

    total = len(suburb_list)
    logger.info(f"Processing {total} suburb records...")

    for index, suburb in enumerate(suburb_list, start=1):
        try:
            # Skip if already exists
            if SuburbLocationData.objects.filter(requested_place=suburb).exists():
                continue

            response = requests.get(base_url, params={
                "q": suburb,
                "key": api_key
            }, timeout=10)

            response.raise_for_status()
            data = response.json()

            if "results" in data and data["results"]:
                first_result = data["results"][0]
                components = first_result.get("components", {})
                formatted = first_result.get("formatted", "")
                country = str(components.get("country", "")).lower()

                if country == "india":
                    road = components.get("road")
                    address = formatted.replace(f"{road},", "").strip() if road else formatted

                    with transaction.atomic():
                        SuburbLocationData.objects.create(
                            address=address,
                            json_data=data,
                            requested_place=suburb
                        )

                    logger.info(f"[{index}/{total}] ✅ Created: {address}")
                    time.sleep(0.5)

                else:
                    logger.warning(f"⚠️ Skipped '{suburb}' — country={country}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network/API error for '{suburb}': {e}")
            time.sleep(2)

        except Exception as e:
            logger.exception(f"Unexpected error for '{suburb}': {e}")
            time.sleep(2)
            continue


def update_suburb_of_indian_locations(batch_size=100):
    # queryset = SuburbLocationData.objects.filter(json_data__isnull=False).order_by("id")[:batch_size]
    queryset = SuburbLocationData.objects.all().order_by("id")[:batch_size]
    total = queryset.count()
    print(f"Processing {total} records...")

    for index, item in enumerate(queryset, start=1):
        
        updating_objs = IndianLocation.objects.filter(suburb=item.requested_place)
        if not updating_objs.exists():
            print(f"⚠️ No IndianLocation found for suburb '{item.requested_place}'")
            continue

        json_data = item.json_data
        if not json_data:
            continue

        
        json_string = str(json_data).encode("utf-8")
        json_hash = hashlib.sha256(json_string).hexdigest()

        
        # if item.json_hash == json_hash:
        #     continue

        results = json_data.get("results")
        if not results:
            continue  

        districts = set()  

        for result in results:
            components = result.get("components", {})
            suburb = components.get("suburb")
            state_district = components.get("state_district")

            if suburb == "R/S Ward":
                print(components)
            
            # if not suburb or not state_district:
            #     continue
            # if suburb.strip().lower() != item.requested_place.strip().lower():
            #     continue

            # districts.add(state_district)

        
        # if len(districts) == 1:
        #     district_value = list(districts)[0]
        #     updated_count = updating_objs.update(
        #         district=district_value,
        #         json_hash=json_hash
        #     )
        #     print(f"✅ Updated {updated_count} rows for suburb '{item.requested_place}' → district '{district_value}'")
        # else:
        #     print(f"⚠️ Skipped '{item.requested_place}' (found {len(districts)} districts: {districts})")

        # print(f"Processed {index}/{total}")