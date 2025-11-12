from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from datetime import datetime
from utility.text import clean_string
from django.http import Http404

from company.models import Company, CompanyType, ContactEnquiry, Client, Testimonial, Banner
from blog.models import Blog
from educational.models import Program
from custom_pages.models import AboutUs
from product.models import Review

from course_api.serializers import ProgramSerializer
from .serializers import (
    CompanySerializer, CompanyTypeSerializer, 
    ContactEnquirySerializer, ClientSerializer, 
    TestimonialSerializer, BannerSerializer, 
    MiniCompanySerializer, MiniCompanyTypeSerializer,
    NavbarCompanyTypeSerializer, LocationBasedFooterCompanyTypeSerializer,
    NormalFooterCompanyTypeSerializer, BaseCompanySerializer, 
    InnerPageCompanySerializer, MinimalCompanySerializer,
    FaqCompanySerializer
    )
from blog_api.serializers import BlogSerializer
from custom_pages_api.serializers import AboutUsSerializer
from product_api.serializers import ReviewSerializer
from custom_pages_api.serializers import ContactUsSerializer
from custom_pages.models import ContactUs

from .paginations import BlogPagination

import logging

logger = logging.getLogger(__name__)

class MinimalCompanyApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = MinimalCompanySerializer
    queryset = Company.objects.all()

    def get_queryset(self):
        company_type = self.request.query_params.get("company_type")
        companies_limit = self.request.query_params.get("companies_limit")

        queryset = self.queryset

        if company_type:
            queryset = Company.objects.filter(type__name = company_type).order_by("?")

            if companies_limit:
                try:
                    limit = int(companies_limit)
                    queryset = queryset[:limit]
                except (TypeError, ValueError):
                    pass

            return queryset
        
        return queryset


class FaqCompanyApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = FaqCompanySerializer
    queryset = Company.objects.all()


class CompanyApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.select_related(
        "type"
    ).prefetch_related(
        "meta_tags", "testimonials"
    ).order_by("?")
    lookup_field  = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class InnerPageCompanyApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = InnerPageCompanySerializer
    queryset = Company.objects.prefetch_related(
        "meta_tags"
    ).order_by("?")
    lookup_field  = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class MiniCompanyApiViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = MiniCompanySerializer
    queryset = Company.objects.all().order_by("?")[:12]
    lookup_field  = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class CompanyTypeApiViewset(viewsets.ModelViewSet):
    serializer_class = CompanyTypeSerializer
    queryset = CompanyType.objects.all().order_by("?")
    lookup_field  = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class NavbarCompanyTypeApiViewset(viewsets.ModelViewSet):
    serializer_class = NavbarCompanyTypeSerializer
    queryset = CompanyType.objects.all().order_by("?")
    lookup_field  = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class FooterCompanyTypeApiViewset(viewsets.GenericViewSet):
    queryset = CompanyType.objects.all().order_by("?")
    lookup_field  = "slug"

    def list(self, request, *args, **kwargs):
        is_location_based = request.query_params.get("location_based")

        company_types = self.queryset

        if is_location_based:

            serializer = LocationBasedFooterCompanyTypeSerializer(
                company_types, many=True, context=self.get_serializer_context()
            )
        else:

            serializer = NormalFooterCompanyTypeSerializer(
                company_types, many=True, context=self.get_serializer_context()
            )

        return Response(serializer.data)
            
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BriefCompanyTypeApiViewset(viewsets.ModelViewSet):
    serializer_class = MiniCompanyTypeSerializer
    queryset = CompanyType.objects.all().order_by("?")[:12]
    lookup_field  = "slug"


class CompanyBlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    pagination_class = BlogPagination
    lookup_field  = "slug"  

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        category = self.request.query_params.get("category")
        month_and_year = self.request.query_params.get("month_and_year")
        s = clean_string(self.request.query_params.get("s", ""))

        if company_slug:        
            filters = Q(company__slug = company_slug, is_published = True)

            if category:
                filters &= (Q(course__name = category) | Q(product__name = category) | Q(service__name = category) | Q(registration__name = category))                

            if month_and_year:
                formated_month_and_year = datetime.strptime(month_and_year, "%B %Y")
                filters &=  Q(
                    published_date__month = formated_month_and_year.month, 
                    published_date__year = formated_month_and_year.year
                    )
                
            if s:
                filters &= (
                        Q(title__icontains = s) | Q(course__name__icontains = s) | 
                        Q(product__name__icontains = s) | Q(service__name__icontains = s) |
                        Q(registration__name__icontains = s) | Q(summary__icontains = s) |
                        Q(content__icontains = s)
                    )
            
            blogs = Blog.objects.filter(filters)

            return blogs      
        
        return Blog.objects.none()
    

class CompanyBlogArchivesViewSets(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        company_slug = self.kwargs.get("company_slug")
        if not company_slug:
            return Response({"message": "Company slug was not provided"}, status=status.HTTP_400_BAD_REQUEST)

        archive = (
            Blog.objects.filter(company__slug=company_slug, is_published=True)
            .annotate(month=TruncMonth("published_date"))
            .values("month")
            .annotate(published_month_count=Count("id"))
            .order_by("-month")
        )

        data = [
            {   
                "endpoint": entry["month"].strftime("%Y/%m"),
                "published_month_and_year": entry["month"].strftime("%B %Y"),
                "published_month_count": entry["published_month_count"],
            }
            for entry in archive
        ]

        return Response(data, status=status.HTTP_200_OK)
    

class CompanyAboutUsViewSet(viewsets.ModelViewSet):
    serializer_class = AboutUsSerializer
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            if company_slug == "bzindia":
                return AboutUs.objects.filter(company__isnull = True)
            
            return AboutUs.objects.filter(company__slug = company_slug)
        
        return AboutUs.objects.none()


class ContactEnquiryViewSet(viewsets.ModelViewSet):
    serializer_class = ContactEnquirySerializer

    def get_queryset(self):
        return ContactEnquiry.objects.filter(company__slug=self.kwargs.get("company_slug")) if self.kwargs.get("company_slug") else ContactEnquiry.objects.none()
    
    def create(self, request, *args, **kwargs):
        response_data = {
            "success": False,
            "message": "Validation Failed",
            "errors": None
        }

        try:
            company_slug = self.kwargs.get("company_slug")
            if not company_slug:
                response_data["message"] = "Company identifier missing"
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            company = get_object_or_404(Company, slug = company_slug)
            
            enquiry_data = request.data.copy()              

            enquiry_data["company"] = company
            serializer = self.get_serializer(data=enquiry_data)
            serializer.is_valid(raise_exception=True)
            
            serializer.save(company = company)

            response_data.update({
                "success": True,
                "message": "Enquiry submitted successfully",
                "data": serializer.data
            })
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Http404:
            response_data.update({
                "message": "Invalid company specified",
                "error": "Company not found"
            })
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except serializers.ValidationError as e:
            response_data.update({
                "message": "Validation error",
                "errors": e.detail
            })
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(
                f"Enquiry submission error - Company: {company_slug}, "
            )
            response_data.update({
                "message": "Server error processing your enquiry",
                "error": "Internal server error"
            })
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyProgramViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProgramSerializer
    queryset = Program.objects.all()
    lookup_field = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    
# class CompanyRegistrationTypeViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = RegistrationTyp
#     queryset = Program.objects.all()
#     lookup_field = "slug"

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         return context
    

class CompanyClientViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClientSerializer
    
    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return Client.objects.filter(company__slug = slug)
        
        return Client.objects.none()


class CompanyTestimonialViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestimonialSerializer
    
    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return Testimonial.objects.filter(company__slug = slug).order_by("order")
        
        return Testimonial.objects.none()
    

class CompanyReviewViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return Review.objects.filter(
                company__slug = slug, company__type__name = "Product"
                ).select_related("user", "product").order_by("order")[0:12]
        
        return Review.objects.none()
    

class CompanyBannerViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = BannerSerializer
    
    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return Banner.objects.filter(company__slug = slug).order_by("-created")
        
        return Banner.objects.none()
    

class CompanyContactUsViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContactUsSerializer
    
    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return ContactUs.objects.filter(company__slug = slug).order_by("-created")
        
        return ContactUs.objects.none()


class BaseCompanyViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = BaseCompanySerializer
    queryset = Company.objects.all()