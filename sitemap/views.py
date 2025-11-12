from rest_framework.decorators import api_view
from rest_framework.response import Response
from product.models import ProductDetailPage, Category as ProductCategory, SubCategory as ProductSubCategory, MultiPage as ProductMultiPage
from service.models import ServiceDetail, Category as ServiceCategory, SubCategory as ServiceSubCategory
from registration.models import RegistrationDetailPage, RegistrationType, RegistrationSubType
from educational.models import CourseDetail, Program, Specialization
from blog.models import Blog
from company.models import Company
from base.models import MetaTag
from locations.models import UniquePlace, UniqueDistrict, UniqueState

def generate_location_url_tails():
    for slug in UniqueState.objects.values_list("slug", flat=True).iterator():
        yield f"/{slug}"

    for state, slug in UniqueDistrict.objects.values_list("state__slug", "slug").iterator():
        yield f"/{state}/{slug}"

    for state, district, slug in UniquePlace.objects.values_list(
        "state__slug", "district__slug", "slug"
    ).iterator():
        yield f"/{state}/{district}/{slug}"

def generate_location_url_slugs():
    for slug in UniqueState.objects.values_list("slug", flat=True).iterator():
        yield slug

    for slug in UniqueDistrict.objects.values_list("slug", flat=True).iterator():
        yield slug

    for slug in UniquePlace.objects.values_list("slug", flat=True).iterator():
        yield slug

@api_view(["GET"])
def product_sitemap_count(request):
    total_places = UniquePlace.objects.count()
    url_tails_count = total_places * 4
    url_place_count = total_places * 2

    company_urls = Company.objects.filter(type__name="Product").count() * 5
    category_urls = ProductCategory.objects.count()
    sub_category_urls = ProductSubCategory.objects.count()
    detail_page_urls = ProductDetailPage.objects.count() * 3
    multi_location_urls = ProductMultiPage.objects.filter(url_type = "location_filtered").count() * url_tails_count
    multi_slug_urls = ProductMultiPage.objects.filter(url_type = "slug_filtered").count() * url_place_count

    total_urls = company_urls + category_urls + sub_category_urls + detail_page_urls + multi_location_urls + multi_slug_urls

    return Response({"total_urls": total_urls})

@api_view(["GET"])
def product_sitemap_urls(request):
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 2000))

    if page_size:
        page_size = 2000

    urls = []

    # 🔹 Companies of type Product
    for c in Company.objects.filter(type__name="Product").values("slug"):
        urls.extend([
            {"loc": f"/{c['slug']}/", "changefreq": "weekly", "priority": 1.0},
            {"loc": f"/{c['slug']}/about-us", "changefreq": "weekly", "priority": 1.0},
            {"loc": f"/{c['slug']}/contact-us", "changefreq": "weekly", "priority": 1.0},
            {"loc": f"/{c['slug']}/faqs", "changefreq": "weekly", "priority": 1.0},
            {"loc": f"/{c['slug']}/learn", "changefreq": "weekly", "priority": 1.0},
        ])

    # 🔹 Product categories
    for category in ProductCategory.objects.values("company__slug", "slug"):
        urls.append({"loc": f"/{category['company__slug']}/{category['slug']}/", "changefreq": "weekly", "priority": 0.6})

    # 🔹 Product subcategories
    for sub_category in ProductSubCategory.objects.values("company__slug", "category__slug", "slug"):
        urls.append({"loc": f"/{sub_category['company__slug']}/{sub_category['category__slug']}/{sub_category['slug']}/", "changefreq": "weekly", "priority": 0.6})

    # 🔹 Product detail pages
    for p in ProductDetailPage.objects.select_related("company", "product__category", "product__sub_category"):
        urls.extend([
            {"loc": f"/{p.company.slug}/{p.product.category.slug}/", "changefreq": "weekly", "priority": 0.9},
            {"loc": f"/{p.company.slug}/{p.product.category.slug}/{p.product.sub_category.slug}/", "changefreq": "weekly", "priority": 0.9},
            {"loc": f"/{p.computed_url}/", "changefreq": "weekly", "priority": 0.9},
        ])

    for p in ProductMultiPage.objects.select_related("company"):
        if p.url_type == "location_filtered":
            url_tails = generate_location_url_tails()

            multi_location_urls = [
                {
                    "loc": f"/{p.company.slug}/{p.slug}{tail}",
                    "changefreq": "weekly",
                    "priority": 0.9,
                }
                for tail in url_tails
            ]

            # Add the base URL
            urls.append(
                {
                    "loc": f"/{p.company.slug}/{p.slug}/",
                    "changefreq": "weekly",
                    "priority": 0.9,
                }
            )

            urls.extend(multi_location_urls)

        else:

            place_slugs = generate_location_url_slugs()

            multi_slug_urls = [
                {
                    "loc": f"/{p.company.slug}/{p.slug.replace('place_name', place_slug)}",
                    "changefreq": "weekly",
                    "priority": 0.9,
                }
                for place_slug in place_slugs
            ]

            urls.append(
                {
                    "loc": f"/{p.company.slug}/{p.slug.replace('place_name', 'india')}/",
                    "changefreq": "weekly",
                    "priority": 0.9,
                }
            )

            urls.extend(multi_slug_urls)


    # 🔹 Paginate URLs
    start = (page - 1) * page_size
    end = start + page_size
    paginated_urls = urls[start:end]

    return Response(paginated_urls)


@api_view(["GET"])
def sitemap_urls(request):
    urls = []

    # 🔹 Static pages
    urls += [
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
        {"loc": "/blog", "changefreq": "weekly", "priority": 0.6},
    ]

    # 🔹 Companies
    for c in Company.objects.select_related("type"):
        urls.append({"loc": f"/{c.slug}/", "changefreq": "weekly", "priority": 1.0})
        urls.append({"loc": f"/{c.slug}/about-us", "changefreq": "weekly", "priority": 1.0})
        urls.append({"loc": f"/{c.slug}/contact-us", "changefreq": "weekly", "priority": 1.0})
        urls.append({"loc": f"/{c.slug}/faqs", "changefreq": "weekly", "priority": 1.0})
        urls.append({"loc": f"/{c.slug}/learn", "changefreq": "weekly", "priority": 1.0})

        if c.type.name == "Education":
            urls.append({"loc": f"/{c.slug}/courses", "changefreq": "weekly", "priority": 1.0})

        elif c.type.name == "Registration":
            urls.append({"loc": f"/{c.slug}/registrations", "changefreq": "weekly", "priority": 1.0})

        elif c.type.name == "Service":
            urls.append({"loc": f"/{c.slug}/services", "changefreq": "weekly", "priority": 1.0})

        elif c.type.name == "Product":
            urls.append({"loc": f"/{c.slug}/products", "changefreq": "weekly", "priority": 1.0})

    # 🔹 Products
    for category in ProductCategory.objects.values("company__slug", "slug"):
        urls.append({"loc": f"/{category['company__slug']}/{category['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for sub_category in ProductSubCategory.objects.values("company__slug", "category__slug", "slug"):
        urls.append({"loc": f"/{sub_category['company__slug']}/{sub_category['category__slug']}/{sub_category['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for p in ProductDetailPage.objects.select_related("company", "product__category", "product__sub_category"):
        urls.append({"loc": f"/{p.company.slug}/{p.product.category.slug}/", "changefreq": "weekly", "priority": 0.9})
        urls.append({"loc": f"/{p.company.slug}/{p.product.category.slug}/{p.product.sub_category.slug}/", "changefreq": "weekly", "priority": 0.9})
        urls.append({"loc": f"/{p.computed_url}/", "changefreq": "weekly", "priority": 0.9})

    # 🔹 Services
    for category in ServiceCategory.objects.values("company__slug", "slug"):
        urls.append({"loc": f"/{category['company__slug']}/{category['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for sub_category in ServiceSubCategory.objects.values("company__slug", "category__slug", "slug"):
        urls.append({"loc": f"/{sub_category['company__slug']}/{sub_category['category__slug']}/{sub_category['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for s in ServiceDetail.objects.select_related("company", "service__category", "service__sub_category"):
        urls.append({"loc": f"/{s.computed_url}/", "changefreq": "weekly", "priority": 0.9})

    # 🔹 Courses
    for program in Program.objects.values("company__slug", "slug"):
        urls.append({"loc": f"/{program['company__slug']}/{program['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for specialization in Specialization.objects.values("company__slug", "program__slug", "slug"):
        urls.append({"loc": f"/{specialization['company__slug']}/{specialization['program__slug']}/{specialization['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for c in CourseDetail.objects.select_related("company", "course__program", "course__specialization"):
        urls.append({"loc": f"/{c.computed_url}/", "changefreq": "weekly", "priority": 0.9})

    # 🔹 Registrations
    for registration_type in RegistrationType.objects.values("company__slug", "slug"):
        urls.append({"loc": f"/{registration_type['company__slug']}/{registration_type['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for sub_type in RegistrationSubType.objects.values("company__slug", "type__slug", "slug"):
        urls.append({"loc": f"/{sub_type['company__slug']}/{sub_type['type__slug']}/{sub_type['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for r in RegistrationDetailPage.objects.select_related("company", "registration__registration_type", "registration__sub_type"):
        urls.append({"loc": f"/{r.computed_url}/", "changefreq": "weekly", "priority": 0.9})

    # 🔹 Blogs
    for b in Blog.objects.values("slug", "company__slug"):
        if b["company__slug"]:
            urls.append({"loc": f"/{b['company__slug']}/learn/{b['slug']}/", "changefreq": "weekly", "priority": 0.6})
        else:
            urls.append({"loc": f"/learn/{b['slug']}/", "changefreq": "weekly", "priority": 0.6})

    # 🔹 Tags
    for t in MetaTag.objects.values("slug"):
        urls.append({"loc": f"/tag/{t['slug']}/", "changefreq": "monthly", "priority": 0.5})

    return Response(urls)



@api_view(["GET"])
def service_sitemap_urls(request):
    urls = []

    for c in Company.objects.filter(type__name = "Service").values("slug"):
        urls.append({"loc": f"/{c['slug']}/", "changefreq": "weekly", "priority": 1.0})
        urls.append({"loc": f"/{c['slug']}/about-us", "changefreq": "weekly", "priority": 1.0})
        urls.append({"loc": f"/{c['slug']}/contact-us", "changefreq": "weekly", "priority": 1.0})
        urls.append({"loc": f"/{c['slug']}/faqs", "changefreq": "weekly", "priority": 1.0})
        urls.append({"loc": f"/{c['slug']}/learn", "changefreq": "weekly", "priority": 1.0})

    for category in ServiceCategory.objects.values("company__slug", "slug"):
        urls.append({"loc": f"/{category['company__slug']}/{category['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for sub_category in ServiceSubCategory.objects.values("company__slug", "category__slug", "slug"):
        urls.append({"loc": f"/{sub_category['company__slug']}/{sub_category['category__slug']}/{sub_category['slug']}/", "changefreq": "weekly", "priority": 0.6})

    for s in ServiceDetail.objects.select_related("company", "service__category", "service__sub_category"):
        urls.append({"loc": f"/{s.computed_url}/", "changefreq": "weekly", "priority": 0.9})