from django.http import HttpResponse
from django.contrib.syndication.views import Feed
from utility.custom_feed import ContentEncodedFeed
from utility.location import get_ip_location, get_nearby_locations
from home.models import HomeContent
from django.shortcuts import get_object_or_404

from product.models import ProductDetailPage, MultiPage as ProductMultiPage
from service.models import ServiceDetail, MultiPage as ServiceMultiPage
from registration.models import RegistrationDetailPage, MultiPage as RegistrationMultiPage
from educational.models import CourseDetail, MultiPage as CourseMultiPage
from locations.models import UniquePlace, UniqueDistrict, UniqueState
from directory.models import Destination
from base.models import MetaTag
from company.models import Testimonial

from django.utils.text import Truncator
from django.utils.html import strip_tags

from locations.trie_cache import get_place_trie, get_district_trie, get_state_trie

from company.models import Company

class DetailFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, type_slug, company_slug, slug):
        company = get_object_or_404(Company, slug=company_slug)

        item = None

        if (company.type.name == "Service"):
            item = get_object_or_404(ServiceDetail, slug=slug, company=company)
        elif (company.type.name == "Education"):
            item = get_object_or_404(CourseDetail, slug=slug, company=company)
        elif (company.type.name == "Registration"):
            item = get_object_or_404(RegistrationDetailPage, slug=slug, company=company)
        elif (company.type.name == "Product"):
            item = get_object_or_404(ProductDetailPage, slug=slug, company=company)

        return item

    def title(self, obj):
        return obj.meta_title

    def link(self, obj):
        return f"/{obj.company.type.slug}/{obj.company.slug}/{obj.slug}/feed/"

    def description(self, obj):
        return obj.meta_description

    def items(self, obj):
        if (obj.company.type.name == "Service"):
            return [obj.service]
        elif (obj.company.type.name == "Education"):
            return [obj.course]
        elif (obj.company.type.name == "Registration"):
            return [obj.registration_sub_type]
        elif (obj.company.type.name == "Product"):
            return [obj.product]

        return [obj]

    def item_title(self, item):
        company_type = item.company.type.name

        if (company_type == "Service"):
            return item.service.meta_title or item.service.name
        elif (company_type == "Education"):
            return item.course.meta_title or item.course.name
        elif (company_type == "Registration"):
            return item.registration_sub_type.meta_title or item.registration_sub_type.name
        elif (company_type == "Product"):
            return item.product.meta_title or item.product.name

        return ""

    def item_description(self, item):
        return item.meta_description or item.name

    def item_link(self, item):
        return f"/{item.company.type.slug}/{item.company.slug}/{item.slug}/"

    def item_pubdate(self, item):
        return item.updated or item.created
    
    def item_enclosure_url(self, item):
        if (item.company.type.name == "Service"):
            return item.service.image.url if item.service.image else None
        elif (item.company.type.name == "Education"):
            return item.course.image.url if item.course.image else None
        elif (item.company.type.name == "Registration"):
            return item.registration_sub_type.image.url if item.registration_sub_type.image else None
        elif (item.company.type.name == "Product"):
            return item.product.image.url if item.product.image else None
        
        return None

    def item_enclosure_length(self, item):
        if (item.company.type.name == "Service"):
            return item.service.image.size if item.service.image else 0
        elif (item.company.type.name == "Education"):
            return item.course.image.size if item.course.image else 0
        elif (item.company.type.name == "Registration"):
            return item.registration_sub_type.image.size if item.registration_sub_type.image else 0
        elif (item.company.type.name == "Product"):
            return item.product.image.size if item.product.image else 0
        
        return 0

    def item_enclosure_mime_type(self, item):
        if (item.company.type.name == "Service"):
            return "image/jpeg" if item.service.image else None
        elif (item.company.type.name == "Education"):
            return "image/jpeg" if item.course.image else None
        elif (item.company.type.name == "Registration"):
            return "image/jpeg" if item.registration_sub_type.image else None
        elif (item.company.type.name == "Product"):
            return "image/jpeg" if item.product.image else None

        return  None

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.description  # Raw HTML content (escaped inside CDATA)
        }

# Optional: Serve with XML stylesheet
class StyledDetailFeed(DetailFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response

MATCH_ORDER = [
    ("state", get_state_trie, UniqueState),
    ("district", get_district_trie, UniqueDistrict),
    ("place", get_place_trie, UniquePlace),
]

def retrieve(slug):                 
    # for model_type, trie, model, serializer_class in MATCH_ORDER:
    for model_type, get_trie_fn, model in MATCH_ORDER:
        trie = get_trie_fn()
        matched_slug = trie.match_suffix(slug)
        if matched_slug:
            try:
                instance = model.objects.get(slug=matched_slug)
                return model_type, instance
                
            except model.DoesNotExist:
                return None, None
        

class MultipageFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug, slug, state_slug=None, location_slug=None):
        company = get_object_or_404(Company, slug=company_slug)        

        self.slug = slug
        self.region_slug = None

        if state_slug and location_slug:
            self.state_slug = state_slug
            self.location_slug = location_slug
        
        else:
            _, location = retrieve(slug)
            self.region_slug = self.slug
            self.slug = slug.replace(location.slug, "place_name")

        item = None

        if (company.type.name == "Service"):
            item = get_object_or_404(ServiceMultiPage, slug=self.slug, company=company)
        elif (company.type.name == "Education"):
            item = get_object_or_404(CourseMultiPage, slug=self.slug, company=company)
        elif (company.type.name == "Registration"):
            item = get_object_or_404(RegistrationMultiPage, slug=self.slug, company=company)
        elif (company.type.name == "Product"):
            item = get_object_or_404(ProductMultiPage, slug=self.slug, company=company)

        return item

    def title(self, obj):
        return obj.meta_title or obj.title

    def link(self, obj):
        if hasattr(self, "state_slug") and hasattr(self, "location_slug") and self.state_slug and self.location_slug:
            return f"/{obj.company.slug}/{obj.slug}/{self.state_slug}/{self.location_slug}/feed/"

        return f"/{obj.company.slug}/{self.region_slug}/feed/"

    def description(self, obj):
        return obj.meta_description or obj.description or obj.summary

    def items(self, obj):
        return [obj]

    def item_title(self, item):
        company_type = item.company.type.name

        if (company_type == "Service"):
            return item.service.name
        elif (company_type == "Education"):
            return item.course.name
        elif (company_type == "Registration"):
            return item.registration_sub_type.name
        elif (company_type == "Product"):
            return item.product.name

        return item.name

    def item_description(self, item):
        return item.meta_description or item.name

    def item_link(self, item):
        if hasattr(self, "state_slug") and hasattr(self, "location_slug") and self.state_slug and self.location_slug:
            return f"/{item.company.slug}/{item.slug}/{self.state_slug}/{self.location_slug}/"

        return f"/{item.company.slug}/{self.region_slug}/"

    def item_pubdate(self, item):
        return item.updated or item.created
    
    def item_enclosure_url(self, item):
        if (item.company.type.name == "Service"):
            return item.service.image.url if item.service.image else None
        elif (item.company.type.name == "Education"):
            return item.course.image.url if item.course.image else None
        elif (item.company.type.name == "Registration"):
            return item.registration_sub_type.image.url if item.registration_sub_type.image else None
        elif (item.company.type.name == "Product"):
            return item.product.image.url if item.product.image else None
        
        return None

    def item_enclosure_length(self, item):
        if (item.company.type.name == "Service"):
            return item.service.image.size if item.service.image else 0
        elif (item.company.type.name == "Education"):
            return item.course.image.size if item.course.image else 0
        elif (item.company.type.name == "Registration"):
            return item.registration_sub_type.image.size if item.registration_sub_type.image else 0
        elif (item.company.type.name == "Product"):
            return item.product.image.size if item.product.image else 0
        
        return 0

    def item_enclosure_mime_type(self, item):
        if (item.company.type.name == "Service"):
            return "image/jpeg" if item.service.image else None
        elif (item.company.type.name == "Education"):
            return "image/jpeg" if item.course.image else None
        elif (item.company.type.name == "Registration"):
            return "image/jpeg" if item.registration_sub_type.image else None
        elif (item.company.type.name == "Product"):
            return "image/jpeg" if item.product.image else None

        return  None

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.description  # Raw HTML content (escaped inside CDATA)
        }

# Optional: Serve with XML stylesheet
class StyledMultipageFeed(MultipageFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response


class ServiceMultipagesFeed(Feed):
    feed_type = ContentEncodedFeed
    link = "/services/feed/"

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def items(self):
        coordinate = get_ip_location(self.request)

        if coordinate:
            lat = coordinate.get("latitude")
            lon = coordinate.get("longitude")

            if lat and lon:
                places = get_nearby_locations(lat, lon)

                services = ServiceMultiPage.objects.filter(available_states = places.first().state).order_by("-updated", "-created")[:12]            

                service_list = []

                for place in places:
                    for service in services:
                        obj_title =service.title.replace("place_name", place.name)
                        obj_meta_title =service.meta_title.replace("place_name", place.name)
                        obj_description =service.description.replace("place_name", place.name)
                        obj_meta_description =service.meta_description.replace("place_name", place.name)
                        obj_slug = service.slug.replace("place_name", place.slug) if service.url_type == "slug_filtered" else f"{service.slug}/{place.state.slug}/{place.slug}"

                        service_list.append({
                            "title": obj_title,
                            "meta_title": obj_meta_title,
                            "description": obj_description,
                            "meta_description": obj_meta_description,
                            "slug": obj_slug,

                            "company__slug": service.company.slug,
                            "url_type": service.url_type,
                            "created": service.created,
                            "updated": service.updated
                        })

                return service_list

        return list(ServiceMultiPage.objects.values(
            "title", "meta_title", "description", "meta_description", "slug", "company__slug",
            "created", "updated", "url_type"
            ).order_by("-updated", "-created")[:12])

    def item_title(self, item):
        return item.get("title")

    def item_description(self, item):
        return Truncator(strip_tags(item.get("meta_description") or item.get("description") or "")).words(50)

    def item_link(self, item):        
        return f"/{item.get('company__slug')}/{item.get('slug')}/" or ""

    def item_pubdate(self, item):
        return item.get("updated") or item.get("created")

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.get("description") or ""
        }

# Optional: Serve with XML stylesheet
class StyledServiceMultipagesFeed(ServiceMultipagesFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class ProductMultipagesFeed(Feed):
    feed_type = ContentEncodedFeed
    link = "/products/feed/"

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def items(self):
        coordinate = get_ip_location(self.request)

        if coordinate:
            lat = coordinate.get("latitude")
            lon = coordinate.get("longitude")

            if lat and lon:
                places = get_nearby_locations(lat, lon)

                products = ProductMultiPage.objects.filter(available_states = places.first().state).order_by("-updated", "-created")[:12]            

                product_list = []

                for place in places:
                    for product in products:
                        obj_title =product.title.replace("place_name", place.name)
                        obj_meta_title =product.meta_title.replace("place_name", place.name)
                        obj_description =product.description.replace("place_name", place.name)
                        obj_meta_description =product.meta_description.replace("place_name", place.name)
                        obj_slug = product.slug.replace("place_name", place.slug) if product.url_type == "slug_filtered" else f"{product.slug}/{place.state.slug}/{place.slug}"

                        product_list.append({
                            "title": obj_title,
                            "meta_title": obj_meta_title,
                            "description": obj_description,
                            "meta_description": obj_meta_description,
                            "slug": obj_slug,

                            "company__slug": product.company.slug,
                            "url_type": product.url_type,
                            "created": product.created,
                            "updated": product.updated
                        })

                return product_list

        return list(ProductMultiPage.objects.values(
            "title", "meta_title", "description", "meta_description", "slug", "company__slug",
            "created", "updated", "url_type"
            ).order_by("-updated", "-created")[:12])

    def item_title(self, item):
        return item.get("title")

    def item_description(self, item):
        return Truncator(strip_tags(item.get("meta_description") or item.get("description") or "")).words(50)

    def item_link(self, item):        
        return f"/{item.get('company__slug')}/{item.get('slug')}/" or ""

    def item_pubdate(self, item):
        return item.get("updated") or item.get("created")

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.get("description") or ""
        }

# Optional: Serve with XML stylesheet
class StyledProductMultipagesFeed(ProductMultipagesFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response


class CourseMultipagesFeed(Feed):
    feed_type = ContentEncodedFeed
    link = "/courses/feed/"

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def items(self):
        coordinate = get_ip_location(self.request)

        if coordinate:
            lat = coordinate.get("latitude")
            lon = coordinate.get("longitude")

            if lat and lon:
                places = get_nearby_locations(lat, lon)

                courses = CourseMultiPage.objects.filter(available_states = places.first().state).order_by("-updated", "-created")[:12]            

                course_list = []

                for place in places:
                    for course in courses:
                        obj_title =course.title.replace("place_name", place.name)
                        obj_meta_title =course.meta_title.replace("place_name", place.name)
                        obj_description =course.description.replace("place_name", place.name)
                        obj_meta_description =course.meta_description.replace("place_name", place.name)
                        obj_slug = course.slug.replace("place_name", place.slug) if course.url_type == "slug_filtered" else f"{course.slug}/{place.state.slug}/{place.slug}"

                        course_list.append({
                            "title": obj_title,
                            "meta_title": obj_meta_title,
                            "description": obj_description,
                            "meta_description": obj_meta_description,
                            "slug": obj_slug,

                            "company__slug": course.company.slug,
                            "url_type": course.url_type,
                            "created": course.created,
                            "updated": course.updated
                        })

                return course_list

        return list(CourseMultiPage.objects.values(
            "title", "meta_title", "description", "meta_description", "slug", "company__slug",
            "created", "updated", "url_type"
            ).order_by("-updated", "-created")[:12])

    def item_title(self, item):
        return item.get("title")

    def item_description(self, item):
        return Truncator(strip_tags(item.get("meta_description") or item.get("description") or "")).words(50)

    def item_link(self, item):        
        return f"/{item.get('company__slug')}/{item.get('slug')}/" or ""

    def item_pubdate(self, item):
        return item.get("updated") or item.get("created")

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.get("description") or ""
        }

# Optional: Serve with XML stylesheet
class StyledCourseMultipagesFeed(CourseMultipagesFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response


class RegistrationMultipagesFeed(Feed):
    feed_type = ContentEncodedFeed
    link = "/registrations/feed/"

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def items(self):
        coordinate = get_ip_location(self.request)

        if coordinate:
            lat = coordinate.get("latitude")
            lon = coordinate.get("longitude")

            if lat and lon:
                places = get_nearby_locations(lat, lon)

                registrations = RegistrationMultiPage.objects.filter(available_states = places.first().state).order_by("-updated", "-created")[:12]            

                registration_list = []

                for place in places:
                    for registration in registrations:
                        obj_title =registration.title.replace("place_name", place.name)
                        obj_meta_title =registration.meta_title.replace("place_name", place.name)
                        obj_description =registration.description.replace("place_name", place.name)
                        obj_meta_description =registration.meta_description.replace("place_name", place.name)
                        obj_slug = registration.slug.replace("place_name", place.slug) if registration.url_type == "slug_filtered" else f"{registration.slug}/{place.state.slug}/{place.slug}"

                        registration_list.append({
                            "title": obj_title,
                            "meta_title": obj_meta_title,
                            "description": obj_description,
                            "meta_description": obj_meta_description,
                            "slug": obj_slug,

                            "company__slug": registration.company.slug,
                            "url_type": registration.url_type,
                            "created": registration.created,
                            "updated": registration.updated
                        })

                return registration_list

        return list(RegistrationMultiPage.objects.values(
            "title", "meta_title", "description", "meta_description", "slug", "company__slug",
            "created", "updated", "url_type"
            ).order_by("-updated", "-created")[:12])

    def item_title(self, item):
        return item.get("title")

    def item_description(self, item):
        return Truncator(strip_tags(item.get("meta_description") or item.get("description") or "")).words(50)

    def item_link(self, item):        
        return f"/{item.get('company__slug')}/{item.get('slug')}/" or ""

    def item_pubdate(self, item):
        return item.get("updated") or item.get("created")

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.get("description") or ""
        }

# Optional: Serve with XML stylesheet
class StyledRegistrationMultipagesFeed(RegistrationMultipagesFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response


class CompanyServicesFeed(Feed):
    feed_type = ContentEncodedFeed    

    def items(self):
        return ServiceDetail.objects.order_by("-updated", "-created")[:20]

    def item_title(self, item):
        return item.meta_title or item.service.name or ""

    def item_description(self, item):
        # You can remove `Truncator(...).words(50)` if you want full content (not recommended for raw HTML)
        return Truncator(strip_tags(item.meta_description or item.description or "")).words(50)

    def item_link(self, item):
        return f"/{item.company.type.slug}/{item.company.slug}/{item.slug}/" or ""

    def item_pubdate(self, item):
        return item.updated or item.created

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.description  # Raw HTML content (escaped inside CDATA)
        }

# Optional: Serve with XML stylesheet
class StyledCompanyServicesFeed(CompanyServicesFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyProductsFeed(Feed):
    feed_type = ContentEncodedFeed
    link = "/products/feed/"

    def items(self):
        return ProductDetailPage.objects.order_by("-updated", "-created")[:20]

    def item_title(self, item):
        return item.meta_title or item.product.name or ""

    def item_description(self, item):
        # You can remove `Truncator(...).words(50)` if you want full content (not recommended for raw HTML)
        return Truncator(strip_tags(item.meta_description or item.description or "")).words(50)

    def item_link(self, item):
        return f"/{item.company.type.slug}/{item.company.slug}/{item.slug}/" or ""

    def item_pubdate(self, item):
        return item.updated or item.created

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.description  # Raw HTML content (escaped inside CDATA)
        }

# Optional: Serve with XML stylesheet
class StyledCompanyProductsFeed(CompanyProductsFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyCoursesFeed(Feed):
    feed_type = ContentEncodedFeed
    link = "/courses/feed/"

    def items(self):
        return CourseDetail.objects.order_by("-updated", "-created")[:20]

    def item_title(self, item):
        return item.meta_title or item.course.name or ""

    def item_description(self, item):
        # You can remove `Truncator(...).words(50)` if you want full content (not recommended for raw HTML)
        return Truncator(strip_tags(item.meta_description or item.description or "")).words(50)

    def item_link(self, item):
        return f"/{item.company.type.slug}/{item.company.slug}/{item.slug}/" or ""

    def item_pubdate(self, item):
        return item.updated or item.created

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.description  # Raw HTML content (escaped inside CDATA)
        }

# Optional: Serve with XML stylesheet
class StyledCompanyCoursesFeed(CompanyCoursesFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyRegistrationsFeed(Feed):
    feed_type = ContentEncodedFeed
    link = "/registrations/feed/"

    def items(self):
        return RegistrationDetailPage.objects.order_by("-updated", "-created")[:20]

    def item_title(self, item):
        return item.meta_title or item.registration_sub_type.name or ""

    def item_description(self, item):
        # You can remove `Truncator(...).words(50)` if you want full content (not recommended for raw HTML)
        return Truncator(strip_tags(item.meta_description or item.description or "")).words(50)

    def item_link(self, item):
        return f"/{item.company.type.slug}/{item.company.slug}/{item.slug}/" or ""

    def item_pubdate(self, item):
        return item.updated or item.created

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.description  # Raw HTML content (escaped inside CDATA)
        }

# Optional: Serve with XML stylesheet
class StyledCompanyRegistrationsFeed(CompanyRegistrationsFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class MetaTagFeed(Feed):
    feed_type = ContentEncodedFeed
    description = "List of all tags used in the site."

    def get_object(self, request, tag_slug=None):        
        self.tag_slug = tag_slug if tag_slug else None

        return get_object_or_404(MetaTag, slug = tag_slug) if tag_slug else None
    
    def description(self):
        if self.tag_slug:
            return f"List of all items connected with {self.tag_slug}"
        
        return "List of all tags used in the site."
    
    def link(self, obj):
        if self.tag_slug:
            return f"/tag/{obj.slug}/feed/"
        
        return "/tag/feed/"
        
    def items(self, obj):
        if obj:
            product_list = ProductDetailPage.objects.filter(meta_tags__slug=obj.slug).values(
                "product__name", "meta_title", "description", "meta_description", "slug", "company__slug", "company__type__slug"
            )
            service_list = ServiceDetail.objects.filter(meta_tags__slug=obj.slug).values(
                "service__name", "meta_title", "description", "meta_description", "slug", "company__slug", "company__type__slug"
            )
            registration_list = RegistrationDetailPage.objects.filter(meta_tags__slug=obj.slug).values(
                "registration_sub_type__name", "meta_title", "description", "meta_description", "slug", "company__slug", "company__type__slug"
            )
            course_list = CourseDetail.objects.filter(meta_tags__slug=obj.slug).values(
                "course__name", "meta_title", "description", "meta_description", "slug", "company__slug", "company__type__slug"
            )

            combined_list = list(product_list) + list(service_list) + list(registration_list) + list(course_list)

            return [
                {
                    "name": item.get("product__name") or item.get("service__name") or item.get("registration_sub_type__name") or item.get("course__name"),
                    "meta_title": item.get("meta_title"),
                    "meta_description": item.get("meta_description"),
                    "description": item.get("description"),
                    "slug": item.get("slug"),
                    "company_slug": item.get("company__slug"),
                    "company_type_slug": item.get("company__type__slug")
                }
                for item in combined_list
            ]

        return MetaTag.objects.all().order_by("name")[:100]

    def item_title(self, item):
        if self.tag_slug:
            return item["meta_title"] or item["name"]

        return item.name

    def item_description(self, item):
        if self.tag_slug:
            return item["meta_description"] or item["description"]

        return f"Tag used in BZ India."

    def item_link(self, item):
        if self.tag_slug:
            return f"/{item['company_type_slug']}/{item['company_slug']}/{item['slug']}"        

        return f"/tag/{item.slug}/"    


# Optional: Serve with XML stylesheet
class StyledMetaTagFeed(MetaTagFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class HomeFeed(Feed):
    feed_type = ContentEncodedFeed
    link = "/feed/"

    def get_object(self, request):
        self.request = request
        return HomeContent.objects.first()

    def title(self, obj):
        return obj.meta_title or "BZ India - Home Feed"

    def description(self, obj):
        return obj.meta_description or obj.description or "Latest updates from the BZ India homepage."

    def items(self, obj):
        coordinate = get_ip_location(self.request)     

        destinations = list(Destination.objects.values(
            "name", "description", "slug", "created", "updated"
            ).order_by("-updated", "-created")[:12])   

        if coordinate:
            lat = coordinate.get("latitude")
            lon = coordinate.get("longitude")

            if lat and lon:
                places = get_nearby_locations(lat, lon)

                service_collection = ServiceMultiPage.objects.filter(available_states = places.first().state).order_by("-updated", "-created")[:12]
                product_collection = ProductMultiPage.objects.filter(available_states = places.first().state).order_by("-updated", "-created")[:12]
                course_collection = CourseMultiPage.objects.filter(available_states = places.first().state).order_by("-updated", "-created")[:12]
                registration_collection = RegistrationMultiPage.objects.filter(available_states = places.first().state).order_by("-updated", "-created")[:12]

                services = []
                products = []
                courses = []
                registrations = []

                for place in places:
                    for service in service_collection:
                        obj_title =service.title.replace("place_name", place.name)
                        obj_meta_title =service.meta_title.replace("place_name", place.name)
                        obj_description =service.description.replace("place_name", place.name)
                        obj_meta_description =service.meta_description.replace("place_name", place.name)
                        obj_slug = service.slug.replace("place_name", place.slug) if service.url_type == "slug_filtered" else f"{service.slug}/{place.state.slug}/{place.slug}"

                        services.append({
                            "title": obj_title,
                            "meta_title": obj_meta_title,
                            "description": obj_description,
                            "meta_description": obj_meta_description,
                            "slug": obj_slug,

                            "company__slug": service.company.slug,
                            "url_type": service.url_type,
                            "created": service.created,
                            "updated": service.updated
                        })

                    for product in product_collection:
                        obj_title =product.title.replace("place_name", place.name)
                        obj_meta_title =product.meta_title.replace("place_name", place.name)
                        obj_description =product.description.replace("place_name", place.name)
                        obj_meta_description =product.meta_description.replace("place_name", place.name)
                        obj_slug = product.slug.replace("place_name", place.slug) if product.url_type == "slug_filtered" else f"{product.slug}/{place.state.slug}/{place.slug}"

                        products.append({
                            "title": obj_title,
                            "meta_title": obj_meta_title,
                            "description": obj_description,
                            "meta_description": obj_meta_description,
                            "slug": obj_slug,

                            "company__slug": product.company.slug,
                            "url_type": product.url_type,
                            "created": product.created,
                            "updated": product.updated
                        })

                    for course in course_collection:
                        obj_title =course.title.replace("place_name", place.name)
                        obj_meta_title =course.meta_title.replace("place_name", place.name)
                        obj_description =course.description.replace("place_name", place.name)
                        obj_meta_description =course.meta_description.replace("place_name", place.name)
                        obj_slug = course.slug.replace("place_name", place.slug) if course.url_type == "slug_filtered" else f"{course.slug}/{place.state.slug}/{place.slug}"

                        courses.append({
                            "title": obj_title,
                            "meta_title": obj_meta_title,
                            "description": obj_description,
                            "meta_description": obj_meta_description,
                            "slug": obj_slug,

                            "company__slug": course.company.slug,
                            "url_type": course.url_type,
                            "created": course.created,
                            "updated": course.updated
                        })

                    for registration in registration_collection:
                        obj_title =registration.title.replace("place_name", place.name)
                        obj_meta_title =registration.meta_title.replace("place_name", place.name)
                        obj_description =registration.description.replace("place_name", place.name)
                        obj_meta_description =registration.meta_description.replace("place_name", place.name)
                        obj_slug = registration.slug.replace("place_name", place.slug) if registration.url_type == "slug_filtered" else f"{registration.slug}/{place.state.slug}/{place.slug}"

                        registrations.append({
                            "title": obj_title,
                            "meta_title": obj_meta_title,
                            "description": obj_description,
                            "meta_description": obj_meta_description,
                            "slug": obj_slug,

                            "company__slug": registration.company.slug,
                            "url_type": registration.url_type,
                            "created": registration.created,
                            "updated": registration.updated
                        })

                return services + products + registrations + courses + destinations

        services = list(ServiceMultiPage.objects.values(
            "title", "meta_title", "description", "meta_description", "slug", "company__slug",
            "created", "updated", "url_type"
            ).order_by("-updated", "-created")[:12])
        products = list(ProductMultiPage.objects.values(
            "title", "meta_title", "description", "meta_description", "slug", "company__slug",
            "created", "updated", "url_type"
            ).order_by("-updated", "-created")[:12])
        registrations = list(RegistrationMultiPage.objects.values(
            "title", "meta_title", "description", "meta_description", "slug", "company__slug",
            "created", "updated", "url_type"
            ).order_by("-updated", "-created")[:12])
        courses = list(CourseMultiPage.objects.values(
            "title", "meta_title", "description", "meta_description", "slug", "company__slug",
            "created", "updated", "url_type"
            ).order_by("-updated", "-created")[:12])                                

        return services + products + registrations + courses + destinations

    def item_title(self, item):
        if item.get("meta_title"):
            return item.get("meta_title") or ""        
        if item.get("name"):
            return item.get("name") or ""
        return "Homepage Item"

    def item_description(self, item):
        desc = item.get("meta_description") or item.get("description") or ""
        return Truncator(strip_tags(desc)).words(40)

    def item_link(self, item):
        if item.get("company__slug") and item.get("slug"):
            return f"/{item.get('company__slug')}/{item.get('slug')}/" or ""
        elif item.get("slug"):
            return f"/destinations/{item.get('slug')}/"
        return "/"

    def item_pubdate(self, item):
        return getattr(item, "updated", None) or getattr(item, "created", None)


class StyledHomeFeed(HomeFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response


class TestimonialFeed(Feed):
    feed_type = ContentEncodedFeed

    title = "Customer Testimonials – BZ India"
    link = "/comments/feed/"
    description = "Latest testimonials from customers of companies listed on BZ India."

    def items(self):
        return Testimonial.objects.order_by("-created")[:20]

    def item_title(self, item):
        return f"Testimonial by {item.name} about company {item.company.name}"

    def item_description(self, item):
        return item.text

    def item_link(self, item):
        return f"/comments/{item.slug}/"  # adjust to your actual URL name

    def item_pubdate(self, item):
        return item.created

# Optional: Serve with XML stylesheet
class StyledTestimonialFeed(TestimonialFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response


def nothing(request):
    result = get_ip_location(request)
    return HttpResponse(f"<h3>{result}</h3>")