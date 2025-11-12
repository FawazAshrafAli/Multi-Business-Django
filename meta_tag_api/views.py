from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import MetaTagSerializer, ItemSerializer
from .paginations import ItemPagination, MetaTagPagination
from company_api.serializers import InnerPageCompanySerializer

from service.models import MetaTag
from blog.models import Blog
from company.models import Company
from product.models import ProductDetailPage, MultiPage as ProductMultiPage
from service.models import ServiceDetail, MultiPage as ServiceMultiPage
from registration.models import RegistrationDetailPage, MultiPage as RegistrationMultiPage
from educational.models import CourseDetail, MultiPage as CourseMultiPage

class MetaTagApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = MetaTagSerializer
    queryset = MetaTag.objects.all().order_by("-updated")
    lookup_field = "slug"
    pagination_class = MetaTagPagination


class MostMatchingCompanyViewSet(viewsets.ReadOnlyModelViewSet):
    model = Company
    serializer_class = InnerPageCompanySerializer
    queryset = Company.objects.none()
    lookup_field = "slug"

    def get_queryset(self):
        slug = self.kwargs.get("slug")

        if not slug:
            return self.queryset
        
        company_slugs = []

        company_slugs += list(ProductDetailPage.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))
        company_slugs += list(ServiceDetail.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))
        company_slugs += list(CourseDetail.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))
        company_slugs += list(RegistrationDetailPage.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))

        company_slugs += list(ProductMultiPage.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))
        company_slugs += list(ServiceMultiPage.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))
        company_slugs += list(CourseMultiPage.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))
        company_slugs += list(RegistrationMultiPage.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))

        company_slugs += list(Blog.objects.filter(meta_tags__slug = slug, company__isnull = False).values_list("company__slug", flat=True))
    
        if len(company_slugs) == 0:
            return self.queryset

        unique_company_slugs = list(set(company_slugs))

        most_repetation = 1
        most_matched_company_slug = company_slugs[0]

        for unique_slug in unique_company_slugs:
            company_count = company_slugs.count(unique_slug)
            
            if company_count > most_repetation:
                most_repetation = company_count
                most_matched_company_slug = unique_slug

        return Company.objects.filter(slug = most_matched_company_slug)            


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = []
    pagination_class = ItemPagination
    serializer_class = ItemSerializer

    def list(self, request, *args, **kwargs):        

        slug = self.kwargs.get("slug")

        if not slug:
            return Response({"items": "Slug is not provided"}, status=status.HTTP_400_BAD_REQUEST)

        items = []

        product_details = ProductDetailPage.objects.filter(meta_tags__slug = slug)
        service_details = ServiceDetail.objects.filter(meta_tags__slug = slug)
        course_details = CourseDetail.objects.filter(meta_tags__slug = slug)
        registration_details = RegistrationDetailPage.objects.filter(meta_tags__slug = slug)

        product_multipages = ProductMultiPage.objects.filter(meta_tags__slug = slug)
        service_multipages = ServiceMultiPage.objects.filter(meta_tags__slug = slug)
        course_multipages = CourseMultiPage.objects.filter(meta_tags__slug = slug)
        registration_multipages = RegistrationMultiPage.objects.filter(meta_tags__slug = slug)

        blogs = Blog.objects.filter(meta_tags__slug = slug)

        items += [{
            "title": detail.product.name,
            "image_url": request.build_absolute_uri(detail.product.image.url) if detail.product.image and detail.product.image.name else "",
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "meta_tags": detail.meta_tags.all(),
            "price": detail.product.price,
            "slug": detail.slug,
            "updated": detail.updated,
            "url_type": None,
            "url": f"{detail.company.slug}/{detail.product.category.slug}/{detail.product.sub_category.slug}/{detail.slug}"        
            } for detail in product_details]        
        
        items += [{
            "title": detail.service.name,
            "image_url": request.build_absolute_uri(detail.service.image.url) if detail.service.image and detail.service.image.name else "",
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "meta_tags": detail.meta_tags.all(),
            "price": detail.service.price,
            "slug": detail.slug,
            "updated": detail.updated,
            "url_type": None,
            "url": f"{detail.company.slug}/{detail.service.category.slug}/{detail.service.sub_category.slug}/{detail.slug}"
            } for detail in service_details]
        
        items += [{
            "title": detail.registration.title,
            "image_url": request.build_absolute_uri(detail.registration.image.url) if detail.registration.image and detail.registration.image.name else "",
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "meta_tags": detail.meta_tags.all(),
            "price": "",
            "slug": detail.slug,
            "updated": detail.updated,
            "url_type": None,
            "url": f"{detail.company.slug}/{detail.registration.registration_type.slug}/{detail.registration.sub_type.slug}/{detail.slug}"
            } for detail in registration_details]
        
        items += [{
            "title": detail.course.name,
            "image_url": request.build_absolute_uri(detail.course.image.url) if detail.course.image and detail.course.image.name else "",
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "meta_tags": detail.meta_tags.all(),
            "price": detail.course.price,
            "slug": detail.slug,    

            "mode": detail.course.mode,
            "start_date": detail.course.starting_date.date() if detail.course.starting_date else None,
            "end_date": detail.course.ending_date.date() if detail.course.ending_date else None,
            "duration": detail.course.duration,
            "category": detail.course.program.name,
            "rating": detail.course.rating,
            "rating_count": detail.course.rating_count,
            "updated": detail.updated,

            "url_type": None,
            "url": f"{detail.company.slug}/{detail.course.program.slug}/{detail.course.specialization.slug}/{detail.slug}"

            } for detail in course_details]
        
        items += [{
            "title": multipage.title,                        
            "image_url": (
                request.build_absolute_uri(first_item.image.url)
                if (first_item := multipage.products.filter(image__isnull = False).exclude(image = "").first())
                else None
            ),
            "summary": multipage.summary,
            "company_name": multipage.company.name,
            "company_type_name": multipage.company.type.name,
            "company_type_slug": multipage.company.type.slug,
            "company_slug": multipage.company.slug,
            "meta_description": multipage.meta_description,
            "meta_tags": multipage.meta_tags.all(),
            "price": multipage.products.values_list("price", flat=True).first(),
            "slug": multipage.slug,
            "updated": multipage.updated,
            "url_type": multipage.url_type,
            "url": f"{multipage.company.slug}/{multipage.slug}"
            } for multipage in product_multipages]
        
        items += [{
            "title": multipage.title,
            "image_url": request.build_absolute_uri(multipage.service.image.url) if multipage.service.image and multipage.service.image.name else "",
            "summary": multipage.summary,
            "company_name": multipage.company.name,
            "company_type_name": multipage.company.type.name,
            "company_type_slug": multipage.company.type.slug,
            "company_slug": multipage.company.slug,
            "meta_description": multipage.meta_description,
            "meta_tags": multipage.meta_tags.all(),
            "price": multipage.service.price,
            "slug": multipage.slug,
            "updated": multipage.updated,
            "url_type": multipage.url_type,
            "url": f"{multipage.company.slug}/{multipage.slug}"
            } for multipage in service_multipages]
        
        items += [{
            "title": multipage.title,
            "image_url": request.build_absolute_uri(multipage.registration.image.url) if multipage.registration.image and multipage.registration.image.name else "",
            "summary": multipage.summary,
            "company_name": multipage.company.name,
            "company_type_name": multipage.company.type.name,
            "company_type_slug": multipage.company.type.slug,
            "company_slug": multipage.company.slug,
            "meta_description": multipage.meta_description,
            "meta_tags": multipage.meta_tags.all(),
            "price": multipage.registration.price,
            "slug": multipage.slug,
            "updated": multipage.updated,
            "url_type": multipage.url_type,
            "url": f"{multipage.company.slug}/{multipage.slug}"
            } for multipage in registration_multipages]
        
        items += [{
            "title": multipage.title,
            "image_url": request.build_absolute_uri(multipage.course.image.url) if multipage.course.image and multipage.course.image.name else "",
            "summary": multipage.summary,
            "company_name": multipage.company.name,
            "company_type_name": multipage.company.type.name,
            "company_type_slug": multipage.company.type.slug,
            "company_slug": multipage.company.slug,
            "meta_description": multipage.meta_description,
            "meta_tags": multipage.meta_tags.all(),
            "price": multipage.course.price,
            "slug": multipage.slug,
            "updated": multipage.updated,
            "url_type": multipage.url_type,
            "url": f"{multipage.company.slug}/{multipage.slug}"
            } for multipage in course_multipages]

        items += [{
            "title": blog.title,
            "image_url": request.build_absolute_uri(blog.image.url) if blog.image and blog.image.name else "",
            "summary": blog.summary,
            "company_name": blog.company.name if blog.company else "BZIndia",
            "company_type_name": blog.company.type.name if blog.company else "",
            "company_type_slug": blog.company.type.slug if blog.company else "",
            "company_slug": blog.company.slug if blog.company else "",
            "meta_description": blog.meta_description,
            "meta_tags": blog.meta_tags.all(),
            "price": "",
            "slug": blog.slug,
            "updated": blog.updated,
            "url_type": "",
            "url": f"{blog.company.slug}/learn/{blog.slug}" if blog.company else f"learn/{blog.slug}"
            } for blog in blogs]
        
        paginated_items = self.paginate_queryset(items)
        serializer = self.get_serializer(paginated_items, many=True)

        return self.get_paginated_response(serializer.data)