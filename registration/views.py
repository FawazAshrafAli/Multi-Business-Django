from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import View
import logging

from superadmin.views import BaseRegistrationCompanyView

from company.models import Company
from registration.models import Registration, RegistrationType, RegistrationSubType, RegistrationDetailPage

logger = logging.getLogger(__name__)

class GetRegistrationTypeView(BaseRegistrationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company_slug")

        if not company_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            current_company = get_object_or_404(Company, slug=company_slug)

            types = RegistrationType.objects.filter(company=current_company).order_by("-created").values("name", "slug")

            return JsonResponse({
                "status": "success",
                "types": list(types)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Error in get function of GetRegistrationTypeView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)
        

class GetRegistrationSubTypeView(BaseRegistrationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)
        
        company_slug = request.GET.get("company_slug")
        type_slug = request.GET.get("type_slug")        

        if not company_slug or not type_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:            

            sub_types = RegistrationSubType.objects.filter(
                company__slug=company_slug, type__slug=type_slug
            ).order_by("-created").values("name", "slug")

            return JsonResponse({
                "status": "success",
                "sub_types": list(sub_types)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or registration type not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetSubTypeView of registration app: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)
        

class GetRegistrationsView(BaseRegistrationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)
        
        company_slug = request.GET.get("company_slug")
        sub_type_slug = request.GET.get("sub_type_slug")        

        if not company_slug or not sub_type_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:            

            registrations = Registration.objects.filter(
                company__slug=company_slug, sub_type__slug=sub_type_slug
            ).order_by("-created").values("title", "slug")

            return JsonResponse({
                "status": "success",
                "registrations": list(registrations)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or registration type not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetRegistrationsView of registration app: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)
        

class GetRegistrationDetailView(BaseRegistrationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company_slug")
        type_slug = request.GET.get("type_slug")
        sub_type_slug = request.GET.get("sub_type_slug")

        if not company_slug or (not type_slug and not sub_type_slug):
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            filters = {"company__slug": company_slug}
            
            if type_slug:
                filters["registration__registration_type__slug"] = type_slug

            if sub_type_slug:
                filters["registration__sub_type__slug"] = sub_type_slug

            registration_details = RegistrationDetailPage.objects.filter(
                **filters
            ).order_by("-created").values("registration__title", "slug")

            return JsonResponse({
                "status": "success",
                "registration_details": list(registration_details)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or registration type not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetSubTypeView of registration app: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)