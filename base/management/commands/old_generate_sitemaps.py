import os
from django.core.management.base import BaseCommand
from django.conf import settings
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
from company.models import Company
from locations.utils.url import generate_location_url_tails, generate_location_url_slugs

PAGE_SIZE = 10000 
# PAGE_SIZE = 49990 

class Command(BaseCommand):
    help = "Generate product and service sitemaps and update sitemap index"

    def handle(self, *args, **kwargs):
        sitemap_files = []

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
            {"loc": "/services", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/products", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/courses", "changefreq": "monthly", "priority": 0.8},
            {"loc": "/registrations", "changefreq": "monthly", "priority": 0.8},
        ]

        for faq in FAQ.objects.filter(company__isnull = True).values("slug"):
            bzindia_urls.append({"loc": f"/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
        
        for blog in Blog.objects.filter(company__isnull = True).values("slug"):
            bzindia_urls.append({"loc": f"/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

        # Write bzindia sitemaps
        sitemap_dir = os.path.join(settings.BASE_DIR, "static", "sitemaps")
        os.makedirs(sitemap_dir, exist_ok=True)
        total_pages = (len(bzindia_urls) + PAGE_SIZE - 1) // PAGE_SIZE

        for page in range(total_pages):
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE
            page_urls = bzindia_urls[start:end]

            filename = "sitemap-bzindia.xml" if page == 0 else f"sitemap-bzindia-{page}.xml"
            sitemap_files.append(filename)
            filepath = os.path.join(sitemap_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
                for u in page_urls:
                    f.write("  <url>\n")
                    f.write(f"    <loc>{settings.SITE_URL}{u['loc']}</loc>\n")
                    f.write(f"    <changefreq>{u['changefreq']}</changefreq>\n")
                    f.write(f"    <priority>{u['priority']}</priority>\n")
                    f.write("  </url>\n")
                f.write("</urlset>\n")
            self.stdout.write(f"Generated {filename} with {len(page_urls)} URLs")

        # -----------------------------
        # 🔹 PRODUCT SITEMAPS
        # -----------------------------
        product_urls = []

        # Companies of type Product
        for company in Company.objects.filter(type__name="Product").values("slug"):
            product_urls.extend([
                {"loc": f"/{company['slug']}/", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/about-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/contact-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/faqs", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/learn", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/products", "changefreq": "weekly", "priority": 1.0},
            ])

            for faq in FAQ.objects.filter(company__slug = company['slug']).values("slug"):
                product_urls.append({"loc": f"/{company['slug']}/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
            
            for blog in Blog.objects.filter(company__slug = company['slug']).values("slug"):
                product_urls.append({"loc": f"/{company['slug']}/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

        # Product categories
        for category in ProductCategory.objects.values("company__slug", "slug"):
            product_urls.append({"loc": f"/{category['company__slug']}/{category['slug']}/", "changefreq": "weekly", "priority": 0.6})

        # Product subcategories
        for sub_category in ProductSubCategory.objects.values("company__slug", "category__slug", "slug"):
            product_urls.append({"loc": f"/{sub_category['company__slug']}/{sub_category['category__slug']}/{sub_category['slug']}/", "changefreq": "weekly", "priority": 0.6})

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

        # Write product sitemaps
        sitemap_dir = os.path.join(settings.BASE_DIR, "static", "sitemaps")
        os.makedirs(sitemap_dir, exist_ok=True)
        total_pages = (len(product_urls) + PAGE_SIZE - 1) // PAGE_SIZE

        for page in range(total_pages):
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE
            page_urls = product_urls[start:end]

            filename = "sitemap-products.xml" if page == 0 else f"sitemap-products-{page}.xml"
            sitemap_files.append(filename)
            filepath = os.path.join(sitemap_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
                for u in page_urls:
                    f.write("  <url>\n")
                    f.write(f"    <loc>{settings.SITE_URL}{u['loc']}</loc>\n")
                    f.write(f"    <changefreq>{u['changefreq']}</changefreq>\n")
                    f.write(f"    <priority>{u['priority']}</priority>\n")
                    f.write("  </url>\n")
                f.write("</urlset>\n")
            self.stdout.write(f"Generated {filename} with {len(page_urls)} URLs")

        # -----------------------------
        # 🔹 Registration SITEMAPS
        # -----------------------------
        registration_urls = []

        # Companies of type Registration
        for company in Company.objects.filter(type__name="Registration").values("slug"):
            registration_urls.extend([
                {"loc": f"/{company['slug']}/", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/about-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/contact-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/faqs", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/learn", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/registrations", "changefreq": "weekly", "priority": 1.0},
            ])

            for faq in FAQ.objects.filter(company__slug = company['slug']).values("slug"):
                registration_urls.append({"loc": f"/{company['slug']}/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
            
            for blog in Blog.objects.filter(company__slug = company['slug']).values("slug"):
                registration_urls.append({"loc": f"/{company['slug']}/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

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

        # Write registration sitemaps
        sitemap_dir = os.path.join(settings.BASE_DIR, "static", "sitemaps")
        os.makedirs(sitemap_dir, exist_ok=True)
        total_pages = (len(registration_urls) + PAGE_SIZE - 1) // PAGE_SIZE

        for page in range(total_pages):
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE
            page_urls = registration_urls[start:end]

            filename = "sitemap-registrations.xml" if page == 0 else f"sitemap-registrations-{page}.xml"
            sitemap_files.append(filename)
            filepath = os.path.join(sitemap_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
                for u in page_urls:
                    f.write("  <url>\n")
                    f.write(f"    <loc>{settings.SITE_URL}{u['loc']}</loc>\n")
                    f.write(f"    <changefreq>{u['changefreq']}</changefreq>\n")
                    f.write(f"    <priority>{u['priority']}</priority>\n")
                    f.write("  </url>\n")
                f.write("</urlset>\n")
            self.stdout.write(f"Generated {filename} with {len(page_urls)} URLs")

        # -----------------------------
        # 🔹 Course SITEMAPS
        # -----------------------------
        course_urls = []

        # Companies of type Course
        for company in Company.objects.filter(type__name="Education").values("slug"):
            course_urls.extend([
                {"loc": f"/{company['slug']}/", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/about-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/contact-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/faqs", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/learn", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/courses", "changefreq": "weekly", "priority": 1.0},
            ])

            for faq in FAQ.objects.filter(company__slug = company['slug']).values("slug"):
                course_urls.append({"loc": f"/{company['slug']}/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
            
            for blog in Blog.objects.filter(company__slug = company['slug']).values("slug"):
                course_urls.append({"loc": f"/{company['slug']}/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

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

        # Write course sitemaps
        sitemap_dir = os.path.join(settings.BASE_DIR, "static", "sitemaps")
        os.makedirs(sitemap_dir, exist_ok=True)
        total_pages = (len(course_urls) + PAGE_SIZE - 1) // PAGE_SIZE

        for page in range(total_pages):
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE
            page_urls = course_urls[start:end]

            filename = "sitemap-courses.xml" if page == 0 else f"sitemap-courses-{page}.xml"
            sitemap_files.append(filename)
            filepath = os.path.join(sitemap_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
                for u in page_urls:
                    f.write("  <url>\n")
                    f.write(f"    <loc>{settings.SITE_URL}{u['loc']}</loc>\n")
                    f.write(f"    <changefreq>{u['changefreq']}</changefreq>\n")
                    f.write(f"    <priority>{u['priority']}</priority>\n")
                    f.write("  </url>\n")
                f.write("</urlset>\n")
            self.stdout.write(f"Generated {filename} with {len(page_urls)} URLs")

        # -----------------------------
        # 🔹 SERVICE SITEMAPS
        # -----------------------------
        service_urls = []

        # Companies of type Service
        for company in Company.objects.filter(type__name="Service").values("slug"):
            service_urls.extend([
                {"loc": f"/{company['slug']}/", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/about-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/contact-us", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/faqs", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/learn", "changefreq": "weekly", "priority": 1.0},
                {"loc": f"/{company['slug']}/more-services", "changefreq": "weekly", "priority": 1.0},
            ])

            for faq in FAQ.objects.filter(company__slug = company['slug']).values("slug"):
                service_urls.append({"loc": f"/{company['slug']}/faqs/{faq['slug']}/", "changefreq": "weekly", "priority": 1.0},)
            
            for blog in Blog.objects.filter(company__slug = company['slug']).values("slug"):
                service_urls.append({"loc": f"/{company['slug']}/learn/{blog['slug']}/", "changefreq": "weekly", "priority": 1.0},)

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

        # Write service sitemaps
        total_pages = (len(service_urls) + PAGE_SIZE - 1) // PAGE_SIZE

        for page in range(total_pages):
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE
            page_urls = service_urls[start:end]

            filename = "sitemap-services.xml" if page == 0 else f"sitemap-services-{page}.xml"
            sitemap_files.append(filename)
            filepath = os.path.join(sitemap_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
                for u in page_urls:
                    f.write("  <url>\n")
                    f.write(f"    <loc>{settings.SITE_URL}{u['loc']}</loc>\n")
                    f.write(f"    <changefreq>{u['changefreq']}</changefreq>\n")
                    f.write(f"    <priority>{u['priority']}</priority>\n")
                    f.write("  </url>\n")
                f.write("</urlset>\n")
            self.stdout.write(f"Generated {filename} with {len(page_urls)} URLs")

        # -----------------------------
        # 🔹 LOCATION SITEMAPS
        # -----------------------------
        location_urls = [{"loc": "/state-list-in-india/", "changefreq": "monthly", "priority": 0.8}]
        location_tails = generate_location_url_tails()

        for tail in location_tails:
            location_urls.append(
                {"loc": f"/state-list-in-india{tail}/", "changefreq": "monthly", "priority": 0.8}
            )

        # Write location sitemaps
        total_pages = (len(location_urls) + PAGE_SIZE - 1) // PAGE_SIZE

        for page in range(total_pages):
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE
            page_urls = location_urls[start:end]

            filename = "sitemap-india.xml" if page == 0 else f"sitemap-india-{page}.xml"
            sitemap_files.append(filename)
            filepath = os.path.join(sitemap_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
                for u in page_urls:
                    f.write("  <url>\n")
                    f.write(f"    <loc>{settings.SITE_URL}{u['loc']}</loc>\n")
                    f.write(f"    <changefreq>{u['changefreq']}</changefreq>\n")
                    f.write(f"    <priority>{u['priority']}</priority>\n")
                    f.write("  </url>\n")
                f.write("</urlset>\n")
            self.stdout.write(f"Generated {filename} with {len(page_urls)} URLs")

        # -----------------------------
        # 🔹 Update sitemap index
        # -----------------------------
        index_filepath = os.path.join(sitemap_dir, "sitemap_index.xml")
        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            for fname in sitemap_files:
                f.write("  <sitemap>\n")
                f.write(f"    <loc>{settings.SITE_URL}/{fname}</loc>\n")
                f.write("  </sitemap>\n")
            f.write("</sitemapindex>\n")

        self.stdout.write(f"Updated sitemap index with {len(sitemap_files)} sitemaps")
