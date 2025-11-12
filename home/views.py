from django.views.generic import TemplateView
import logging

from company.models import Company
from product.models import Product
from service.models import Service
from registration.models import Registration
from educational.models import Course
from blog.models import Blog
from base.models import MetaTag
from django.db.models import Q


from base.views import BaseView

logger = logging.getLogger(__name__)

class HomeView(BaseView, TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["home_page"] = True
            context["companies"] = Company.objects.all().order_by("name")
            context["courses"] = Course.objects.all().order_by("?")[:12]
            context["registration_details"] = Registration.objects.all().order_by("sub_type__name")[:12]
            context["services"] = Service.objects.all().order_by("?")[:12]
            context["products"] = Product.objects.all().order_by("?")[:12]
            context["slider_blogs"] = Blog.objects.filter(is_published = True).order_by("?")[:3]
            context["tags"] = MetaTag.objects.all()
        except Exception as e:
            logger.error(f"Error in fetching the context data of home view: {e}")
        return context


from .models import Village, Coordinates
from locations.models import UniquePlace
from django.core.cache import cache
import requests, os, time

def fetch_coordinates():

    base_url = 'https://api.opencagedata.com/geocode/v1/json'
    api_key = os.getenv('OPENCAGE_API_KEY_3')
    cache_key = f"opencage_requested_{time.strftime('%Y%m%d')}"
    request_count = cache.get(cache_key)
    if request_count is None:
        request_count = 0
        cache.set(cache_key, 0, timeout=60*60*24)

    state_name = "Tamil Nadu"

    villages = Village.objects.filter(state_name = state_name)

    for village in villages:
        # if UniquePlace.objects.filter(
        #     name=village.name,
        #     district__name=village.district_name,
        #     state__name=village.state_name
        # ).exists():
        #     continue    

        if Coordinates.objects.filter(village_code=village.code).exists():
            continue

        if request_count < 20000:
            try:
                # logger.info(f"Querying Place: ({village.name}, {village.district_name}, {village.state_name})")
                print(f"Querying Place: ({village.name}, {village.district_name}, {village.state_name})")

                response = requests.get(base_url, params={
                    "q": f"{village.name}, {village.district_name}, {village.state_name}, India",
                    "key": api_key
                })

                response.raise_for_status()

                request_count += 1
                cache.set(cache_key, request_count, timeout=60*60*24)
                data = response.json()

                # logger.info(f"Request number: {request_count}")
                print(f"Request number: {request_count}")

                if "results" in data and data["results"]:
                    first_result = data["results"][0]
                    components = first_result.get("components", {})

                    country = components.get("country")                    

                    if str(country).lower() in {"india"}:

                        Coordinates.objects.create(                                        
                            json_data = data, 

                            village_code = village.code, village_name = village.name,
                            sub_district_code = village.sub_district_code, sub_district_name = village.sub_district_name,
                            district_code = village.district_code, district_name = village.district_name,
                            state_code = village.state_code, state_name = village.state_name
                        )

                        # logger.info(f"Coordinates fetched for: '{village.name}, {village.district_name}, {village.state_name}'\n")
                        print(f"Coordinates fetched for: '{village.name}, {village.district_name}, {village.state_name}'\n")
                

            except requests.exceptions.RequestException as e:
                # logger.info(f"Error during API request: {e}")
                print(f"Error during API request: {e}")
                time.sleep(0.4)
                continue

            except Exception as e:
                # logger.exception(f"An Unexpected Error occured: {e}")
                print(f"An Unexpected Error occured: {e}")
                time.sleep(0.4)
                continue
    
            time.sleep(0.4)

        else:
            # logger.info("You have used up your daily API call limit.")
            print("You have used up your daily API call limit.")
            return       


# def import_coordinates(batch_size=500):
#     # Filter only villages that need coordinates (uncomment for real run)
#     # villages_qs = Village.objects.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))

#     # For testing single village
#     villages_qs = Village.objects.filter(name="Perinthalmanna")

#     villages_qs.update(latitude = None, longitude = None)

#     total = villages_qs.count()
#     print(f"Total villages to update: {total}")

#     updated = 0
#     to_update = []

#     for index, village in enumerate(villages_qs.iterator(), start=1):
#         print(f"\n➡️ Processing village: {village.name}, {village.district_name}, {village.state_name}")

#         # Get the first created matching Place (even if duplicates exist)
#         place = (
#             Place.objects
#             .select_related('district', 'state')
#             .filter(
#                 name=village.name.strip(),
#                 district__name=village.district_name.strip(),
#                 state__name=village.state_name.strip()
#             )
#             .order_by('created')  # pick the earliest created duplicate
#             .first()
#         )

#         if not place:
#             print(f"⚠️ No matching Place found for: {village.name}")
#             continue

#         if place.latitude is not None and place.longitude is not None:
#             village.latitude = place.latitude
#             village.longitude = place.longitude
#             village.is_old_coordinate = True
#             to_update.append(village)
#             updated += 1
#             print(f"✅ Coordinates copied: ({place.latitude}, {place.longitude}) from Place ID {place.id}")
#         else:
#             print(f"⚠️ Place found but has no coordinates: {place.name}")

#         # Bulk update every batch_size entries
#         if len(to_update) >= batch_size:
#             Village.objects.bulk_update(to_update, ["latitude", "longitude"])
#             to_update.clear()

#         # Progress display every 100 iterations or at the end
#         if index % 100 == 0 or index == total:
#             progress = (index / total) * 100
#             print(f"Progress: {progress:.2f}%  ({index}/{total})")

#     # Final flush
#     if to_update:
#         Village.objects.bulk_update(to_update, ["latitude", "longitude"])

#     print(f"\n✅ Finished! Updated {updated} villages with coordinates.")
