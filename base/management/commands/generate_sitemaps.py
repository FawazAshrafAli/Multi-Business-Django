import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q
from product.models import (
    ProductDetailPage, Category as ProductCategory, SubCategory as ProductSubCategory, MultiPage as ProductMultiPage
)
from service.models import (
    ServiceDetail, Category as ServiceCategory, SubCategory as ServiceSubCategory, MultiPage as ServiceMultiPage
)
from registration.models import (
    RegistrationDetailPage, RegistrationType, RegistrationSubType, MultiPage as RegistrationMultiPage
)
from educational.models import (
    CourseDetail, Program, Specialization, MultiPage as CourseMultiPage
)
from custom_pages.models import FAQ
from blog.models import Blog
from base.models import MetaTag
from company.models import Company
from directory.models import CscCenter
from locations.utils.url import (
    generate_location_url_tails, generate_location_url_slugs, generate_district_slugs, 
    generate_state_slugs, generate_place_dicts, generate_district_dicts, generate_state_dicts
    )
from django.utils import timezone
from pathlib import Path
try:
    from django.contrib.sites.models import Site
    SITES_AVAILABLE = True
except Exception:
    SITES_AVAILABLE = False

PAGE_SIZE = 49990 

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def canonical_base_url() -> str:
    """
    Decide, once, what base URL to use in <loc>:
    1) Sites framework id=1 (recommended) -> https://<domain>
    2) settings.SITE_URL
    3) env SITEMAP_BASE
    4) final fallback 'https://bzindia.in'
    """
    # 1) Sites preferred (id=1 configured to bzindia.in)
    if SITES_AVAILABLE:
        try:
            site_id = getattr(settings, "SITE_ID", 1)
            domain = Site.objects.get(pk=site_id).domain.strip()
            if domain:
                return f"https://{domain.rstrip('/')}"
        except Exception:
            pass

    # 2) settings.SITE_URL
    base = getattr(settings, "SITE_URL", "") or ""
    if base:
        return base.rstrip("/")

    # 3) explicit env override
    env_base = os.getenv("SITEMAP_BASE", "").strip()
    if env_base:
        return env_base.rstrip("/")

    # 4) fallback
    return "https://bzindia.in"


def write_urlset(filepath: Path, base: str, urls: list[dict]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)

    base = base.rstrip("/")
    lastmod = timezone.now().replace(microsecond=0).isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            f.write("  <url>\n")
            f.write(f"    <loc>{base}{u['loc']}</loc>\n")
            f.write(f"    <lastmod>{lastmod}</lastmod>\n")
            f.write(f"    <changefreq>{u['changefreq']}</changefreq>\n")
            f.write(f"    <priority>{u['priority']}</priority>\n")
            f.write("  </url>\n")
        f.write("</urlset>\n")


def chunk_write(sitemap_dir: Path, base: str, urls: list[dict], stem: str, out_names: list[str]):
    total_pages = (len(urls) + PAGE_SIZE - 1) // PAGE_SIZE
    for page in range(total_pages):
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_urls = urls[start:end]
        filename = f"{stem}.xml" if page == 0 else f"{stem}-{page}.xml"
        write_urlset(sitemap_dir / filename, base, page_urls)
        out_names.append(filename)

def write_index(sitemap_dir: Path, base: str, filenames: list[str]) -> None:
    path = sitemap_dir / "sitemap_index.xml"
    base = base.rstrip("/")
    lastmod = timezone.now().replace(microsecond=0).isoformat()

    with open(path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for name in filenames:
            # IMPORTANT: always public base here
            f.write("  <sitemap>\n")
            f.write(f"    <loc>{base}/{name}</loc>\n")
            f.write(f"    <lastmod>{lastmod}</lastmod>\n")
            f.write("  </sitemap>\n")
        f.write("</sitemapindex>\n")

def normalize(s):
    if not s:
        return s
    return s.strip().lower()

class Command(BaseCommand):
    help = "Generate all sitemaps and a sitemap_index.xml using the public domain."
        

    def handle(self, *args, **kwargs):
        base = canonical_base_url()  # e.g. https://bzindia.in
        # Keep writing to the same directory you already expose at /sitemap-*.xml
        sitemap_dir = Path(settings.BASE_DIR) / "static" / "sitemaps"
        out_files: list[str] = []

        # -----------------------------
        # 🔹 BZINDIA SITEMAPS
        # -----------------------------

        bzindia_urls = [
            {"loc": "/", "changefreq": "daily", "priority": 1.0},
            {"loc": "/about-us", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/contact-us", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/faqs", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/learn", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/privacy-policy", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/terms-conditions", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/shipping-delivery-policy", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/cancellation-refund-policy", "changefreq": "monthly", "priority": 0.8},
            # {"loc": "/services", "changefreq": "monthly", "priority": 0.8},
            # {"loc": "/products", "changefreq": "monthly", "priority": 0.8},
            # {"loc": "/courses", "changefreq": "monthly", "priority": 0.8},
            # {"loc": "/registrations", "changefreq": "monthly", "priority": 0.8},
        ]

        for faq in FAQ.objects.filter(company__isnull = True).values("slug"):
            bzindia_urls.append({"loc": f"/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
        
        for blog in Blog.objects.filter(company__isnull = True).values("slug"):
            bzindia_urls.append({"loc": f"/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

        chunk_write(sitemap_dir, base, bzindia_urls, "sitemap-bzindia", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ bzindia: {len(bzindia_urls)} urls"))

        # -----------------------------
        # 🔹 PRODUCT SITEMAPS
        # -----------------------------
        product_urls: list[dict] = []

        # Companies of type Product
        for company in Company.objects.filter(type__name="Product").values("slug"):
            slug = company["slug"]
            product_urls.extend([
                {"loc": f"/{slug}/", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/about-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/contact-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/faqs", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/learn", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/products", "changefreq": "weekly", "priority": 1.0},
            ])

            for faq in FAQ.objects.filter(company__slug = slug).values("slug"):
                product_urls.append({"loc": f"/{slug}/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0})            
            for blog in Blog.objects.filter(company__slug = slug).values("slug"):
                product_urls.append({"loc": f"/{slug}/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0})

        # Product categories
        for category in ProductCategory.objects.values("company__slug", "slug"):
            product_urls.append({"loc": f"/{category['company__slug']}/{category['slug']}/", "changefreq": "weekly", "priority": 0.6})

        # Product subcategories
        for sub_category in ProductSubCategory.objects.values("company__slug", "category__slug", "slug"):
            product_urls.append({
                "loc": f"/{sub_category['company__slug']}/{sub_category['category__slug']}/{sub_category['slug']}/", 
                "changefreq": "weekly", 
                "priority": 0.6
                }
            )

        # Product detail pages
        for detail in ProductDetailPage.objects.select_related("company", "product__category", "product__sub_category"):
            product_urls.extend([
                {"loc": f"/{detail.company.slug}/{detail.product.category.slug}/", "changefreq": "weekly", "priority": 0.9},
                {"loc": f"/{detail.company.slug}/{detail.product.category.slug}/{detail.product.sub_category.slug}/", "changefreq": "weekly", "priority": 0.9},
                {"loc": f"/{detail.computed_url}/", "changefreq": "weekly", "priority": 0.9},
            ])

        # Product multi-pages
        for multipage in ProductMultiPage.objects.select_related("company"):
            available_states_ids = list(multipage.available_states.values_list("id", flat=True))

            if multipage.url_type == "location_filtered":
                tails = generate_location_url_tails(state_ids=available_states_ids)
                product_urls.append({"loc": f"/{multipage.company.slug}/{multipage.slug}/", "changefreq": "weekly", "priority": 0.9})
                product_urls.extend([{"loc": f"/{multipage.company.slug}/{multipage.slug}{tail}", "changefreq": "weekly", "priority": 0.9} for tail in tails])
            else:
                place_slugs = generate_location_url_slugs(state_ids=available_states_ids)
                if "place_name" in multipage.slug:
                    product_urls.append({"loc": f"/{multipage.company.slug}/{multipage.slug.replace('place_name', 'india')}/", "changefreq": "weekly", "priority": 0.9})
                    product_urls.extend([{"loc": f"/{multipage.company.slug}/{multipage.slug.replace('place_name', place_slug)}", "changefreq": "weekly", "priority": 0.9} for place_slug in place_slugs])        

        chunk_write(sitemap_dir, base, product_urls, "sitemap-products", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ products: {len(product_urls)} urls"))

        # -----------------------------
        # 🔹 Registration SITEMAPS
        # -----------------------------
        registration_urls: list[dict] = []

        # Companies of type Registration
        for company in Company.objects.filter(type__name="Registration").values("slug"):
            slug = company["slug"]
            registration_urls.extend([
                {"loc": f"/{slug}/", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/about-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/contact-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/faqs", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/learn", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/registrations", "changefreq": "weekly", "priority": 1.0},
            ])

            for faq in FAQ.objects.filter(company__slug = slug).values("slug"):
                registration_urls.append({"loc": f"/{slug}/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
            
            for blog in Blog.objects.filter(company__slug = slug).values("slug"):
                registration_urls.append({"loc": f"/{slug}/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

        # Registration categories
        for reg_type in RegistrationType.objects.values("company__slug", "slug"):
            registration_urls.append({"loc": f"/{reg_type['company__slug']}/{reg_type['slug']}/", "changefreq": "weekly", "priority": 0.6})

        # Registration subcategories
        for sub_type in RegistrationSubType.objects.values("company__slug", "type__slug", "slug"):
            registration_urls.append({"loc": f"/{sub_type['company__slug']}/{sub_type['type__slug']}/{sub_type['slug']}/", "changefreq": "weekly", "priority": 0.6})

        # Registration detail pages
        for detail in RegistrationDetailPage.objects.select_related("company", "registration__registration_type", "registration__sub_type"):
            registration_urls.extend([
                {"loc": f"/{detail.company.slug}/{detail.registration.registration_type.slug}/", "changefreq": "weekly", "priority": 0.9},
                {"loc": f"/{detail.company.slug}/{detail.registration.registration_type.slug}/{detail.registration.sub_type.slug}/", "changefreq": "weekly", "priority": 0.9},
                {"loc": f"/{detail.computed_url}/", "changefreq": "weekly", "priority": 0.9},
            ])

        # Registration multi-pages
        for multipage in RegistrationMultiPage.objects.select_related("company"):
            available_states_ids = list(multipage.available_states.values_list("id", flat=True))

            if multipage.url_type == "location_filtered":
                tails = generate_location_url_tails(state_ids=available_states_ids)
                registration_urls.append({"loc": f"/{multipage.company.slug}/{multipage.slug}/", "changefreq": "weekly", "priority": 0.9})
                registration_urls.extend([{"loc": f"/{multipage.company.slug}/{multipage.slug}{tail}", "changefreq": "weekly", "priority": 0.9} for tail in tails])
            else:
                place_slugs = generate_location_url_slugs(state_ids=available_states_ids)
                if "place_name" in multipage.slug:
                    registration_urls.append({"loc": f"/{multipage.company.slug}/{multipage.slug.replace('place_name', 'india')}/", "changefreq": "weekly", "priority": 0.9})
                    registration_urls.extend([{"loc": f"/{multipage.company.slug}/{multipage.slug.replace('place_name', place_slug)}", "changefreq": "weekly", "priority": 0.9} for place_slug in place_slugs])

        chunk_write(sitemap_dir, base, registration_urls, "sitemap-registrations", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ registrations: {len(registration_urls)} urls"))        

        # -----------------------------
        # 🔹 Course SITEMAPS
        # -----------------------------
        course_urls: list[dict] = []

        # Companies of type Course
        for company in Company.objects.filter(type__name="Education").values("slug"):
            slug = company["slug"]
            course_urls.extend([
                {"loc": f"/{slug}/", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/about-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/contact-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/faqs", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/learn", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/courses", "changefreq": "weekly", "priority": 1.0},
            ])

            for faq in FAQ.objects.filter(company__slug = slug).values("slug"):
                course_urls.append({"loc": f"/{slug}/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
            
            for blog in Blog.objects.filter(company__slug = slug).values("slug"):
                course_urls.append({"loc": f"/{slug}/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

        # Course categories
        for program in Program.objects.values("company__slug", "slug"):
            course_urls.append({"loc": f"/{program['company__slug']}/{program['slug']}/", "changefreq": "weekly", "priority": 0.6})

        # Course subcategories
        for specialization in Specialization.objects.values("company__slug", "program__slug", "slug"):
            course_urls.append({"loc": f"/{specialization['company__slug']}/{specialization['program__slug']}/{specialization['slug']}/", "changefreq": "weekly", "priority": 0.6})

        # Course detail pages
        for detail in CourseDetail.objects.select_related("company", "course__program", "course__specialization"):
            course_urls.extend([
                {"loc": f"/{detail.company.slug}/{detail.course.program.slug}/", "changefreq": "weekly", "priority": 0.9},
                {"loc": f"/{detail.company.slug}/{detail.course.program.slug}/{detail.course.specialization.slug}/", "changefreq": "weekly", "priority": 0.9},
                {"loc": f"/{detail.computed_url}/", "changefreq": "weekly", "priority": 0.9},
            ])

        # Course multi-pages
        for multipage in CourseMultiPage.objects.select_related("company"):
            available_states_ids = list(multipage.available_states.values_list("id", flat=True))

            if multipage.url_type == "location_filtered":
                tails = generate_location_url_tails(state_ids=available_states_ids)
                course_urls.append({"loc": f"/{multipage.company.slug}/{multipage.slug}/", "changefreq": "weekly", "priority": 0.9})
                course_urls.extend([{"loc": f"/{multipage.company.slug}/{multipage.slug}{tail}", "changefreq": "weekly", "priority": 0.9} for tail in tails])
            else:
                place_slugs = generate_location_url_slugs(state_ids=available_states_ids)
                if "place_name" in multipage.slug:
                    course_urls.append({"loc": f"/{multipage.company.slug}/{multipage.slug.replace('place_name', 'india')}/", "changefreq": "weekly", "priority": 0.9})
                    course_urls.extend([{"loc": f"/{multipage.company.slug}/{multipage.slug.replace('place_name', place_slug)}", "changefreq": "weekly", "priority": 0.9} for place_slug in place_slugs])

        chunk_write(sitemap_dir, base, course_urls, "sitemap-courses", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ courses: {len(course_urls)} urls"))

        # -----------------------------
        # 🔹 SERVICE SITEMAPS
        # -----------------------------
        service_urls: list[dict] = []

        # Companies of type Service
        for company in Company.objects.filter(type__name="Service").values("slug"):
            slug = company["slug"]
            service_urls.extend([
                {"loc": f"/{slug}/", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/about-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/contact-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/faqs", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/learn", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{slug}/more-services", "changefreq": "weekly", "priority": 1.0},
            ])

            for faq in FAQ.objects.filter(company__slug = slug).values("slug"):
                service_urls.append({"loc": f"/{slug}/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
            
            for blog in Blog.objects.filter(company__slug = slug).values("slug"):
                service_urls.append({"loc": f"/{slug}/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

        # Service categories
        for category in ServiceCategory.objects.values("company__slug", "slug"):
            service_urls.append({"loc": f"/{category['company__slug']}/{category['slug']}/", "changefreq": "weekly", "priority": 0.6})

        # Service subcategories
        for sub_category in ServiceSubCategory.objects.values("company__slug", "category__slug", "slug"):
            service_urls.append({"loc": f"/{sub_category['company__slug']}/{sub_category['category__slug']}/{sub_category['slug']}/", "changefreq": "weekly", "priority": 0.6})

        # Service detail pages
        for detail in ServiceDetail.objects.select_related("company", "service__category", "service__sub_category"):
            service_urls.extend([
                {"loc": f"/{detail.company.slug}/{detail.service.category.slug}/", "changefreq": "weekly", "priority": 0.9},
                {"loc": f"/{detail.company.slug}/{detail.service.category.slug}/{detail.service.sub_category.slug}/", "changefreq": "weekly", "priority": 0.9},
                {"loc": f"/{detail.computed_url}/", "changefreq": "weekly", "priority": 0.9},
            ])

        # Service multi-pages
        for multipage in ServiceMultiPage.objects.select_related("company"):
            available_states_ids = list(multipage.available_states.values_list("id", flat=True))

            if multipage.url_type == "location_filtered":
                tails = generate_location_url_tails(state_ids=available_states_ids)
                service_urls.append({"loc": f"/{multipage.company.slug}/{multipage.slug}/", "changefreq": "weekly", "priority": 0.9})
                service_urls.extend([{"loc": f"/{multipage.company.slug}/{multipage.slug}{tail}", "changefreq": "weekly", "priority": 0.9} for tail in tails])
            else:
                place_slugs = generate_location_url_slugs(state_ids=available_states_ids)
                if "place_name" in multipage.slug:
                    service_urls.append({"loc": f"/{multipage.company.slug}/{multipage.slug.replace('place_name', 'india')}/", "changefreq": "weekly", "priority": 0.9})
                    service_urls.extend([{"loc": f"/{multipage.company.slug}/{multipage.slug.replace('place_name', place_slug)}", "changefreq": "weekly", "priority": 0.9} for place_slug in place_slugs])

        chunk_write(sitemap_dir, base, service_urls, "sitemap-services", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ services: {len(service_urls)} urls"))        

        # -----------------------------
        # 🔹 LOCATION SITEMAPS
        # -----------------------------
        location_urls = [{"loc": "/state-list-in-india/", "changefreq": "monthly", "priority": 0.8}]
        location_tails = generate_location_url_tails()

        for tail in location_tails:
            location_urls.append(
                {"loc": f"/state-list-in-india{tail}/", "changefreq": "monthly", "priority": 0.8}
            )

        chunk_write(sitemap_dir, base, location_urls, "sitemap-india", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ locations: {len(location_urls)} urls"))                

        # -----------------------------
        # 🔹 Tags SITEMAPS
        # -----------------------------
        tag_urls = [{"loc": "/tag/", "changefreq": "monthly", "priority": 0.8}]

        location_tag_objs = MetaTag.objects.filter(name__icontains = "place_name", slug__icontains = "place_name")
        location_tag_obj_ids = list(location_tag_objs.values_list("id", flat=True))

        location_tag_slugs = list(location_tag_objs.values_list("slug", flat=True))
        non_location_tag_slugs = list(MetaTag.objects.exclude(id__in = location_tag_obj_ids).values_list("slug", flat=True))

        for tag_slug in non_location_tag_slugs:
            tag_urls.append(
                {"loc": f"/tag/{tag_slug}/", "changefreq": "monthly", "priority": 0.8}
            )

        place_slugs = [slug for slug in generate_location_url_slugs() if slug]

        for tag_slug in location_tag_slugs:
            for place_slug in place_slugs:
                tag_urls.append(
                    {"loc": f"/tag/{tag_slug.replace('place_name', place_slug)}/", "changefreq": "monthly", "priority": 0.8}
                )

        chunk_write(sitemap_dir, base, tag_urls, "sitemap-tag", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ tags: {len(tag_urls)} urls")) 

        # -----------------------------
        # 🔹 State SITEMAPS
        # -----------------------------
        state_urls = []
        state_slugs = generate_state_slugs()

        for slug in state_slugs:
            state_urls.append(
                {"loc": f"/{slug}/", "changefreq": "monthly", "priority": 0.8}
            )

        chunk_write(sitemap_dir, base, state_urls, "sitemap-state", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ states: {len(state_urls)} urls"))
        
        # -----------------------------
        # 🔹 District SITEMAPS
        # -----------------------------
        district_urls = []
        district_slugs = generate_district_slugs()

        for slug in district_slugs:
            district_urls.append(
                {"loc": f"/{slug}/", "changefreq": "monthly", "priority": 0.8}
            )

        chunk_write(sitemap_dir, base, district_urls, "sitemap-district", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ districts: {len(district_urls)} urls"))

        # -----------------------------
        # 🔹 Registration Sub Type Listing
        # -----------------------------
        sub_type_listing_urls = []
        state_slugs = generate_state_slugs()
        district_slugs = generate_district_slugs()
        district_dicts = generate_district_dicts()

        sub_types = RegistrationSubType.objects.values("slug", "location_slug")

        for state_slug in state_slugs:
            sub_type_listing_urls.append(
                {"loc": f"/{state_slug}/filings", "changefreq": "monthly", "priority": 0.8}
            )

            for sub_type in sub_types.iterator():
                page_slug = sub_type["location_slug"] or sub_type["slug"]

                sub_type_listing_urls.append(
                    {"loc": f"/{state_slug}/filings/{page_slug}-{state_slug}", "changefreq": "monthly", "priority": 0.8}
                )

        for district_slug in district_slugs:
            sub_type_listing_urls.append(
                {"loc": f"/{district_slug}/filings", "changefreq": "monthly", "priority": 0.8}
            )

        for district in district_dicts:
            for sub_type in sub_types.iterator():
                page_slug = sub_type["location_slug"] or sub_type["slug"]

                sub_type_listing_urls.append(
                    {"loc": f"/{district['state_slug']}/filings/{page_slug}-{district['slug']}", "changefreq": "monthly", "priority": 0.8}
                )

        chunk_write(sitemap_dir, base, sub_type_listing_urls, "sitemap-registration-sub-type", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ Registration Sub Type Listing: {len(sub_type_listing_urls)} urls"))

        # -----------------------------
        # 🔹 Product Sub Category Listing
        # -----------------------------
        product_sub_category_listing_urls = []
        state_slugs = generate_state_slugs()
        district_slugs = generate_district_slugs()
        district_dicts = generate_district_dicts()

        sub_categories = ProductSubCategory.objects.values("slug", "location_slug")

        for state_slug in state_slugs:
            product_sub_category_listing_urls.append(
                {"loc": f"/{state_slug}/products", "changefreq": "monthly", "priority": 0.8}
            )

            for sub_category in sub_categories.iterator():
                page_slug = sub_category["location_slug"] or sub_category["slug"]

                product_sub_category_listing_urls.append(
                    {"loc": f"/{state_slug}/products/{page_slug}-{state_slug}", "changefreq": "monthly", "priority": 0.8}
                )

        for district_slug in district_slugs:
            product_sub_category_listing_urls.append(
                {"loc": f"/{district_slug}/products", "changefreq": "monthly", "priority": 0.8}
            )

        for district in district_dicts:
            for sub_category in sub_categories.iterator():
                page_slug = sub_category["location_slug"] or sub_category["slug"]

                product_sub_category_listing_urls.append(
                    {"loc": f"/{district['state_slug']}/products/{page_slug}-{district['slug']}", "changefreq": "monthly", "priority": 0.8}
                )

        chunk_write(sitemap_dir, base, product_sub_category_listing_urls, "sitemap-product-sub-category", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ Product Sub Category Listing: {len(product_sub_category_listing_urls)} urls"))

        # -----------------------------
        # 🔹 Service Sub Category Listing
        # -----------------------------
        service_sub_category_listing_urls = []
        state_slugs = generate_state_slugs()
        district_slugs = generate_district_slugs()
        district_dicts = generate_district_dicts()

        sub_categories = ServiceSubCategory.objects.values("slug", "location_slug")

        for state_slug in state_slugs:
            service_sub_category_listing_urls.append(
                {"loc": f"/{state_slug}/more-services", "changefreq": "monthly", "priority": 0.8}
            )

            for sub_category in sub_categories.iterator():
                page_slug = sub_category["location_slug"] or sub_category["slug"]

                service_sub_category_listing_urls.append(
                    {"loc": f"/{state_slug}/more-services/{page_slug}-{state_slug}", "changefreq": "monthly", "priority": 0.8}
                )

        for district_slug in district_slugs:
            service_sub_category_listing_urls.append(
                {"loc": f"/{district_slug}/more-services", "changefreq": "monthly", "priority": 0.8}
            )

        for district in district_dicts:
            for sub_category in sub_categories.iterator():
                page_slug = sub_category["location_slug"] or sub_category["slug"]

                service_sub_category_listing_urls.append(
                    {"loc": f"/{district['state_slug']}/more-services/{page_slug}-{district['slug']}", "changefreq": "monthly", "priority": 0.8}
                )

        chunk_write(sitemap_dir, base, service_sub_category_listing_urls, "sitemap-service-sub-category", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ Service Sub Category Listing: {len(service_sub_category_listing_urls)} urls"))

        # -----------------------------
        # 🔹 Course Specialization Listing
        # -----------------------------
        specification_listing_urls = []
        state_slugs = generate_state_slugs()
        district_slugs = generate_district_slugs()
        district_dicts = generate_district_dicts()

        specializations = Specialization.objects.values("slug", "location_slug")

        for state_slug in state_slugs:
            specification_listing_urls.append(
                {"loc": f"/{state_slug}/courses", "changefreq": "monthly", "priority": 0.8}
            )

            for specialization in specializations.iterator():
                page_slug = specialization["location_slug"] or specialization["slug"]

                specification_listing_urls.append(
                    {"loc": f"/{state_slug}/courses/{page_slug}-{state_slug}", "changefreq": "monthly", "priority": 0.8}
                )

        for district_slug in district_slugs:
            specification_listing_urls.append(
                {"loc": f"/{district_slug}/courses", "changefreq": "monthly", "priority": 0.8}
            )

        for district in district_dicts:
            for specialization in specializations.iterator():
                page_slug = specialization["location_slug"] or specialization["slug"]

                specification_listing_urls.append(
                    {"loc": f"/{district['state_slug']}/courses/{page_slug}-{district['slug']}", "changefreq": "monthly", "priority": 0.8}
                )

        chunk_write(sitemap_dir, base, specification_listing_urls, "sitemap-course-specialization", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ Course Specialization Listing: {len(specification_listing_urls)} urls"))

        # -----------------------------
        # 🔹 CSC Listing
        # -----------------------------
        center_urls = []
        state_slugs = generate_state_slugs()
        district_slugs = generate_district_slugs()
        district_dicts = generate_district_dicts()
        place_dicts = generate_place_dicts()

        state_lookup = {
            normalize(item["name"]): item["slug"]
            for item in generate_state_dicts()
        }        

        district_lookup = {
            f"{normalize(item['name'])}-{normalize(item['state_name'])}": item["slug"]
            for item in generate_district_dicts()
        }

        state_csc_centers = CscCenter.objects.filter(district_name__isnull = True, state_name__isnull = False).values("slug", "state_name")
        district_csc_centers = CscCenter.objects.filter(district_name__isnull = False, state_name__isnull = False).values("slug", "district_name", "state_name")        

        for state_slug in state_slugs:
            center_urls.append(
                {"loc": f"/{state_slug}/csc/", "changefreq": "monthly", "priority": 0.8}
            )

        for slug in district_slugs:
            center_urls.append(
                {"loc": f"/{slug}/csc/", "changefreq": "monthly", "priority": 0.8}
            )

        for district in district_dicts:
            center_urls.append(
                {"loc": f"/{district['state_slug']}/csc/common-service-center-{district['slug']}", "changefreq": "monthly", "priority": 0.8}
            )

        for place in place_dicts:
            center_urls.append(
                {"loc": f"/{place['district_slug']}/csc/common-service-center-{place['slug']}", "changefreq": "monthly", "priority": 0.8}
            )

        for center in state_csc_centers:
            center_state_name = center.get("state_name")
            if not center_state_name:
                continue
            state_slug = normalize(state_lookup.get(center_state_name))
            if state_slug:
                center_urls.append(
                    {"loc": f"/{state_slug}/csc/{center['slug']}", "changefreq": "monthly", "priority": 0.8}
                )        

        for center in district_csc_centers:            
            district_slug = district_lookup.get(f"{normalize(center['district_name'])}-{normalize(center['state_name'])}")
            if district_slug:
                center_urls.append(
                    {"loc": f"/{district_slug}/csc/{center['slug']}", "changefreq": "monthly", "priority": 0.8}
                )

        chunk_write(sitemap_dir, base, center_urls, "sitemap-csc", out_files)
        self.stdout.write(self.style.SUCCESS(f"✓ CSC Listing: {len(center_urls)} urls"))

        # ───────────────── INDEX ─────────────────
        write_index(sitemap_dir, base, out_files)
        self.stdout.write(self.style.SUCCESS(f"Updated sitemap index with {len(out_files)} files at {sitemap_dir/'sitemap_index.xml'}"))
