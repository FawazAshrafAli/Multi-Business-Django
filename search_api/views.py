from django.db.models import Q

from utility.text import clean_string

from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import ItemSerializer
from .paginations import ItemPagination

from product.models import ProductDetailPage
from service.models import ServiceDetail
from educational.models import CourseDetail
from registration.models import RegistrationDetailPage

class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductDetailPage.objects.none()
    pagination_class = ItemPagination
    serializer_class = ItemSerializer

    def list(self, request, *args, **kwargs):
        query = clean_string(self.request.query_params.get("query", ""))

        if not query:
            return Response({"items": "Query is not provided"}, status=status.HTTP_400_BAD_REQUEST)

        items = []        

        product_details = ProductDetailPage.objects.filter(
            Q(company__name__icontains = query) | Q(product__name__icontains = query) |
            Q(product__description__icontains = query) | Q(product__category__name__icontains = query) |
            Q(product__sub_category__name__icontains = query) | Q(product__brand__name__icontains = query) |
            Q(summary__icontains = query) | Q(description__icontains = query) |
            Q(meta_tags__name__icontains = query)
        ).select_related("product", "company")

        service_details = ServiceDetail.objects.filter(
            Q(company__name__icontains = query) | Q(service__name__icontains = query) |
            Q(service__category__name__icontains = query) | Q(service__sub_category__name__icontains = query) | 
            Q(summary__icontains = query) | Q(description__icontains = query) | 
            Q(meta_tags__name__icontains = query)
        ).select_related("service", "company")

        course_details = CourseDetail.objects.filter(
            Q(company__name__icontains = query) | Q(course__name__icontains = query) |
            Q(course__program__name__icontains = query) | Q(course__specialization__name__icontains = query) | 
            Q(summary__icontains = query) | Q(description__icontains = query) | 
            Q(meta_tags__name__icontains = query)
        ).select_related("course", "company")

        registration_details = RegistrationDetailPage.objects.filter(
            Q(company__name__icontains = query) | Q(registration__title__icontains = query) |
            Q(registration__sub_type__name__icontains = query) | Q(registration__registration_type__name__icontains = query) |
            Q(summary__icontains = query) | Q(description__icontains = query) | 
            Q(meta_tags__name__icontains = query)
        ).select_related("registration", "company")

        items += [{
            "title": detail.product.name,
            "image_url": request.build_absolute_uri(detail.product.image.url) if detail.product.image and detail.product.image.name else "",
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "price": detail.product.price,
            "slug": detail.slug,
            "url": detail.computed_url        
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
            "price": detail.service.price,
            "slug": detail.slug,
            "url": detail.computed_url
            } for detail in service_details]
        
        items += [{
            "title": detail.registration.title,
            "image_url": None,
            "summary": detail.summary,
            "company_name": detail.company.name,
            "company_type_name": detail.company.type.name,
            "company_type_slug": detail.company.type.slug,
            "company_slug": detail.company.slug,
            "meta_description": detail.meta_description,
            "price": "",
            "slug": detail.slug,
            "url": detail.computed_url
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
            "price": detail.course.price,
            "slug": detail.slug,    

            "mode": detail.course.mode,
            "start_date": detail.course.starting_date.date(),
            "end_date": detail.course.ending_date,
            "duration": detail.course.duration,
            "category": detail.course.program.name,
            "rating": detail.course.rating,
            "rating_count": detail.course.rating_count,
            "url": detail.computed_url

            } for detail in course_details]
        
        paginated_items = self.paginate_queryset(items)
        serializer = self.get_serializer(paginated_items, many=True)

        return self.get_paginated_response(serializer.data)