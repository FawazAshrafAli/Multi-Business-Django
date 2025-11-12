from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import ListView, View, DetailView
from django.db.models import Q, Count
import logging

from .models import Product, Category, SubCategory, Brand, Color, Size
from base.views import BaseView
from company.models import Company

from company.views import CompanyBaseView

logger = logging.getLogger(__name__)

class GetCategoriesView(View):
    model = Category

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Method not allowed"}, status=405)    
            
            company_slug = request.GET.get("company_slug")

            if not company_slug:
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            categories = list(self.model.objects.filter(company__slug = company_slug).order_by("-created").values("name", "slug"))

            return JsonResponse({"status": "success", "categories": categories}, status=200)

        except Exception as e:
            logger.exception(f"Error in get function of GetCategoriesView in product app: {e}")
            return JsonResponse({"status": "failed", "error": "An unexpected error occurred."}, status=500)
        

class GetSubCategoriesView(View):
    model = SubCategory

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Method not allowed"}, status=405)    
            
            company_slug = request.GET.get("company_slug")
            category_slug = request.GET.get("category_slug")

            if not company_slug or not category_slug:
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            sub_categories = list(self.model.objects.filter(company__slug = company_slug, category__slug = category_slug).order_by("-created").values("name", "slug"))

            return JsonResponse({"status": "success", "sub_categories": sub_categories}, status=200)

        except Exception as e:
            logger.exception(f"Error in get function of GetSubCategoriesView in product app: {e}")
            return JsonResponse({"status": "failed", "error": "An unexpected error occurred."}, status=500)


class GetProductsView(View):
    model = Product

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get('x-requested-with') != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "error": "Method not allowed"}, status=405)    
            
            company_slug = request.GET.get("company_slug")            
            category_slug = request.GET.get("category_slug")
            sub_category_slug = request.GET.get("sub_category_slug")

            if not company_slug or (not category_slug and not sub_category_slug):
                return JsonResponse({"status": "failed", "error": "Bad Request"}, status=400)
            
            filters = {"company__slug": company_slug}

            if category_slug:
                filters["category__slug"] = category_slug

            if sub_category_slug:
                filters["sub_category__slug"] = sub_category_slug
            
            products = list(self.model.objects.filter(**filters).values("name", "slug").order_by("-created"))

            return JsonResponse({"status": "success", "products": products}, status=200)

        except Exception as e:
            logger.exception(f"Error in get function of GetProductsView in product app: {e}")
            return JsonResponse({"status": "failed", "error": "Some unexpected error occurred."}, status=500)


class HomeView(CompanyBaseView, DetailView):
    model = Company
    template_name = "product/home.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()

        return context