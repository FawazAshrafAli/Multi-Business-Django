from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.http import Http404

from .serializers import (
    SubTypeSerializer, DetailSerializer, TypeSerializer, 
    EnquirySerializer, RegistrationSerializer, 
    MiniDetailSerializer, DetailListSerializer
    )
from company_api.serializers import CompanySerializer

from registration.models import RegistrationSubType, RegistrationDetailPage, RegistrationType, Enquiry, Registration
from company.models import Company

from .paginations import RegistrationPagination

import logging

logger = logging.getLogger(__name__)

class SubTypeViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubTypeSerializer
    pagination_class = RegistrationPagination
    lookup_field = "slug"

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")
        type_slug = self.request.query_params.get("type")
        location_slug = self.request.query_params.get("location_slug")

        if slug: 
            filters = {}

            if slug != "all":
                filters = {"company__slug": slug}

            if type_slug:
                filters["type__slug"] = type_slug 

            if location_slug:
                filters["location_slug"] = location_slug  

            return RegistrationSubType.objects.filter(
                **filters
                ).select_related(
                    "company", "type"
                ).order_by("-updated")
        
        return RegistrationSubType.objects.none()
    

class RegistrationViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationSerializer
    # pagination_class = RegistrationPagination
    lookup_field = "slug"

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug: 
            filters = {"company__slug": slug}

            return Registration.objects.filter(**filters)
        
        return Registration.objects.none()


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.filter(type__name = "Registration")
    lookup_field = "slug"


class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TypeSerializer
    lookup_field = "slug"
    pagination_class = RegistrationPagination

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return RegistrationType.objects.filter(company__slug = slug)
        
        return RegistrationType.objects.none()


class DetailViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailSerializer
    lookup_field = "slug"
    pagination_class = RegistrationPagination

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")
        registration_type = self.request.query_params.get("type")
        sub_type_slug = self.request.query_params.get("sub_type")

        filters = {}
        queryset = RegistrationDetailPage.objects.none()

        if registration_type:       
            filters["registration__registration_type__name"] = registration_type

        if sub_type_slug:       
            filters["registration__sub_type__slug"] = sub_type_slug

        if slug:
            queryset = RegistrationDetailPage.objects.all()

            if slug != "all":
                filters["company__slug"] = slug

        queryset = queryset.filter(**filters)                    

        return queryset.select_related(
            "company", "registration", "registration__sub_type",
            "registration__registration_type"
        ).prefetch_related(
            "features", 
            "vertical_tabs", 
            "horizontal_tabs", 
            "tables", 
            "bullet_points", 
            "timelines", 
            "meta_tags"
        )
    

class DetailListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailListSerializer
    lookup_field = "slug"
    pagination_class = RegistrationPagination

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")
        registration_type = self.request.query_params.get("type")
        sub_type_slug = self.request.query_params.get("sub_type")        

        filters = {}
        queryset = RegistrationDetailPage.objects.none()

        if registration_type:       
            filters["registration__registration_type__name"] = registration_type

        if sub_type_slug:       
            filters["registration__sub_type__slug"] = sub_type_slug

        if slug:
            queryset = RegistrationDetailPage.objects.all()

            if slug != "all":
                filters["company__slug"] = slug  

            queryset = queryset.filter(**filters)  

        return queryset.select_related(
                "company", "registration"
            )
    

class DetailSliderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MiniDetailSerializer
    lookup_field = "slug"
    pagination_class = RegistrationPagination

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")        

        if slug:
            if slug == "all":
                return (
                    RegistrationDetailPage.objects.select_related("registration")
                    .only(
                        "id", "slug", "meta_description",
                        "meta_title", "registration"
                        )
                    .order_by("?")[:12]
                )

            filters = {"company__slug": slug}          

            details = (
                RegistrationDetailPage.objects.filter(**filters)
                .select_related("registration")
                .only(
                    "id", "slug", "meta_description",
                    "meta_title", "registration"
                    )
                .order_by("?")[:12]
                )

            return details
        
        return RegistrationDetailPage.objects.none()


class EnquiryViewSet(viewsets.ModelViewSet):
    serializer_class = EnquirySerializer
    http_method_names = ["post", "get"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Enquiry.objects.filter(company__slug=self.kwargs.get("company_slug")) if self.kwargs.get("company_slug") else Enquiry.objects.none()

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
            print(e)

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