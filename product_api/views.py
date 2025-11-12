from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Q, Count

from company_api.serializers import CompanySerializer
from .serializers import (
    ProductCategorySerializer, DetailSerializer, ProductSerializer, 
    EnquirySerializer, ProductSubCategorySerializer, ReviewSerializer,
    MultiPageSerializer, MiniProductDetailSerializer, DetailListSerializer,
    MiniProductCategorySerializer, HomeProductCategorySerializer
    )
from product.models import (
    ProductDetailPage, Category, Product, Enquiry, SubCategory, 
    Review, MultiPage
    )
from company.models import Company
from .paginations import ProductDetailPagination

import logging

logger = logging.getLogger(__name__)

class ProductCompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.filter(type__name = "Product").order_by("name")
    lookup_field = "slug"


class ProductViewset(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")        

        if company_slug:
            return Product.objects.filter(company__slug = company_slug)
        
        return Product.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductDetailViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailSerializer
    pagination_class = ProductDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        q = self.request.query_params.get("q")
        catalog = self.request.query_params.get("catalog")
        category = self.request.query_params.get("category")
        sub_category = self.request.query_params.get("sub_category")

        if company_slug:
            if company_slug == "all":
                return ProductDetailPage.objects.all()

            filters = {"company__slug": company_slug}
            
            if category:
                filters["product__category__slug"] = category

            if sub_category:
                filters["product__sub_category__slug"] = sub_category

            if catalog:
                filters["product__sub_category__slug"] = catalog

            details = ProductDetailPage.objects.filter(**filters)

            if q:
                details = details.filter(
                    Q(product__name__icontains = q) |
                    Q(product__category__name__icontains = q) |
                    Q(product__sub_category__name__icontains = q) |
                    Q(product__brand__name__icontains = q)
                )

            return details.select_related(
                "product", "company"
            ).prefetch_related(
                "meta_tags", "features", "bullet_points", "timelines",
            )
        
        return ProductDetailPage.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class DetailListViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetailListSerializer
    pagination_class = ProductDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        q = self.request.query_params.get("q")
        catalog = self.request.query_params.get("catalog")
        category = self.request.query_params.get("category")
        sub_category = self.request.query_params.get("sub_category")

        filters = {}
        queryset = ProductDetailPage.objects.none()

        print("Entered")
        print(self.kwargs)
        print(self.request.query_params)

        if category:
            filters["product__category__slug"] = category

        if sub_category or catalog:
            filters["product__sub_category__slug"] = sub_category or catalog        

        if company_slug:
            queryset = ProductDetailPage.objects.all()

            if company_slug != "all":
                filters["company__slug"] = company_slug

            queryset = queryset.filter(**filters)   

        if q:
            queryset = queryset.filter(
                Q(product__name__icontains = q) |
                Q(product__category__name__icontains = q) |
                Q(product__sub_category__name__icontains = q) |
                Q(product__brand__name__icontains = q)
            )         

        return queryset.select_related(
                "company", "product"
            )
    

class ProductSliderDetailViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = MiniProductDetailSerializer
    pagination_class = ProductDetailPagination
    lookup_field = "slug"

    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")        

        if company_slug:
            if company_slug == "all":
                return (
                    ProductDetailPage.objects.select_related("product")
                    .only(
                        "id", "slug", "meta_description",
                        "meta_title", "product"
                        )
                    .order_by("?")[:12]
                )

            filters = {"company__slug": company_slug}                        

            details = (
                ProductDetailPage.objects.filter(**filters)
                .select_related("product")
                .only(
                    "id", "slug", "meta_description",
                    "meta_title", "product"
                    )
                .order_by("?")[:12]
                )

            return details
        
        return ProductDetailPage.objects.none()
    

class MinProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MiniProductCategorySerializer
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            return Category.objects.filter(
                company__slug = company_slug
                ).select_related(
                    "company"
                )
        
        return Category.objects.none()


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductCategorySerializer
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            return Category.objects.filter(
                company__slug = company_slug
            ).select_related(
                "company"
            )
        
        return Category.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class HomeProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HomeProductCategorySerializer
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            return Category.objects.filter(
                company__slug = company_slug
            ).select_related(
                "company"
            )
        
        return Category.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class ProductMultipageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MultiPageSerializer
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")

        if company_slug:
            return MultiPage.objects.filter(
                company__slug = company_slug
            ).select_related(
                "product", "company"
            ).prefetch_related(
                "meta_tags", "features", "bullet_points", "timelines", "faqs",
                "text_editors"
            )
            
        return MultiPage.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class ProductSubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSubCategorySerializer
    pagination_class = ProductDetailPagination
    lookup_field = "slug"
    
    def get_queryset(self):
        company_slug = self.kwargs.get("company_slug")
        category_slug = self.request.query_params.get("category")

        if company_slug:
            filters = {}

            if company_slug != "all":
                filters = {"company__slug": company_slug}

            if category_slug:
                filters["category__slug"] = category_slug                   

            return SubCategory.objects.annotate(count = Count("products")).filter(
                **filters
                ).filter(
                    count__gt = 0
                ).select_related(
                    "company", "category"
                ).order_by("created")
        
        return SubCategory.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

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


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    http_method_names = ["post", "get"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Review.objects.filter(company__slug=self.kwargs.get("company_slug")) if self.kwargs.get("company_slug") else Review.objects.none()

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
            
            review_data = request.data.copy()
            review_data["company"] = company
            serializer = self.get_serializer(data=review_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(company = company)

            response_data.update({
                "success": True,
                "message": "Review submitted successfully",
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
                f"Review submission error - Company: {company_slug}, "
            )
            response_data.update({
                "message": "Server error processing your review",
                "error": "Internal server error"
            })
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)