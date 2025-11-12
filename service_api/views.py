from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.http import Http404
from django.shortcuts import get_object_or_404

from .serializers import (
    ServiceSerializer, DetailSerializer, EnquirySerializer, SubCategorySerializer, 
    CategorySerializer, MiniDetailSerializer, DetailListSerializer
    )
from company_api.serializers import CompanySerializer

from service.models import Service, ServiceDetail, Enquiry, SubCategory, Category
from company.models import Company

from .paginations import ServiceDetailPagination

import logging

logger = logging.getLogger(__name__)

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.filter(type__name = "Service")
    lookup_field = "slug"


class ServiceViewset(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            return Service.objects.filter(company__slug = slug)
        
        return Service.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CategoryViewset(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = ServiceDetailPagination
    lookup_field = "slug"
    
    def get_queryset(self):
        slug = self.kwargs.get("company_slug")

        if slug:
            filters = {"company__slug": slug}

            return Category.objects.filter(
                **filters
                ).select_related("company")
        
        return Category.objects.none()


class SubCategoryViewset(viewsets.ModelViewSet):
    serializer_class = SubCategorySerializer
    pagination_class = ServiceDetailPagination
    lookup_field = "slug"
    
    def get_queryset(self):
        slug = self.kwargs.get("company_slug")
        category_slug = self.request.query_params.get("category")

        if slug:
            filters = {}

            if slug != "all":
                filters = {"company__slug": slug}

            if category_slug:
                filters["category__slug"] = category_slug            

            return SubCategory.objects.filter(
                **filters
                ).select_related(
                    "company", "category"
                ).order_by("-updated")
        
        return SubCategory.objects.none()
    

class DetailViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailSerializer
    pagination_class = ServiceDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")
        category_name = self.request.query_params.get("category")
        sub_category_slug = self.request.query_params.get("sub_category")

        filters = {}
        queryset = ServiceDetail.objects.none()

        if category_name:
            filters["service__category__name"] = category_name

        if sub_category_slug:
            filters["service__sub_category__slug"] = sub_category_slug

        if slug:
            queryset = ServiceDetail.objects.all()

            if slug != "all":
                filters["company__slug"] = slug

        queryset = queryset.filter(**filters)
            
        return queryset.select_related(
            "company", "service", "service__sub_category",
            "service__category"
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
    pagination_class = ServiceDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")
        category_name = self.request.query_params.get("category")
        sub_category_slug = self.request.query_params.get("sub_category")

        filters = {}
        queryset = ServiceDetail.objects.none()

        if category_name:
            filters["service__category__name"] = category_name

        if sub_category_slug:
            filters["service__sub_category__slug"] = sub_category_slug

        if slug:
            queryset = ServiceDetail.objects.all()

            if slug != "all":
                filters["company__slug"] = slug

            queryset = queryset.filter(**filters)

        return queryset.select_related(
                "company", "service"
            )
    

class ServiceSliderDetailViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MiniDetailSerializer
    pagination_class = ServiceDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        slug = self.kwargs.get("company_slug")        

        if slug:
            if slug == "all":
                return (
                    ServiceDetail.objects.select_related("service")
                    .only(
                        "id", "slug", "meta_description",
                        "meta_title", "service"
                        )
                    .order_by("?")[:12]
                    )
                

            filters = {"company__slug": slug}      

            details = (
                ServiceDetail.objects.filter(**filters)
                .select_related("service")
                .only(
                    "id", "slug", "meta_description",
                    "meta_title", "service"
                    )
                .order_by("?")[:12]
                )

            return details
        
        return ServiceDetail.objects.none()


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