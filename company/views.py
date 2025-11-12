from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, View
from django.http import JsonResponse, Http404
from blog.models import Blog
import logging

from company.models import Company

from base.views import BaseView

logger = logging.getLogger(__name__)

class CompanyBaseView(BaseView):
    def get_company(self, company_slug):
        try:
            return get_object_or_404(Company, slug = company_slug)
        except Http404:
            return None


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["company_page"] = True
        context["slider_blogs"] = Blog.objects.filter(is_published = True).order_by("?")[:3]

        return context


def get_company(request, slug):
    data = {}
    
    try:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            company = get_object_or_404(Company, slug = slug)
            company = {
                "name": company.name
            }

            data = {"company": company}
    
    except Http404:
        data = {"error": "Invalid Company"}

    except Exception as e:
        msg = "Error in getting the requested company"
        logger.exception(f"{msg}: {e}")
        data = {"error": msg}
        
    return JsonResponse(data)


class GetFilteredCompaniesView(View):
    model = Company

    def get(self, request, *args, **kwargs):
        try:
            if request.headers.get("x-requested-with") != "XMLHttpRequest":
                return JsonResponse({"status": "failed", "message": "Method not allowed"}, status=403)

            company_type = request.GET.get("company_type")

            if not company_type:
                return JsonResponse({"status": "failed", "message": "Bad Request"}, status=400)
            
            companies = list(Company.objects.filter(type__name = company_type).order_by("-created").values("name", "slug"))

            return JsonResponse({"companies": companies, "status": "success"}, status=200)
        
        except Exception as e:
            logger.exception(f"Error in get function of GetFilteredCompaniesView in company app: {e}")
            return JsonResponse({"status": "failed", "message": "An unexpected error occurred"}, status=500)
