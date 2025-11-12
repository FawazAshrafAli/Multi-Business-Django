from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import View, DetailView
import logging

from superadmin.views import BaseEducationCompanyView

from .models import Program, Specialization, Course, Testimonial, Faq, CourseDetail
from company.models import Company, Client
from base.models import MetaTag

from company.views import CompanyBaseView
    
logger = logging.getLogger(__name__)

class GetProgramsView(BaseEducationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company")        

        if not company_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            education_company = get_object_or_404(Company, slug=company_slug, type__name = "Education")

            programs = Program.objects.filter(company=education_company).order_by("-created").values("name", "slug")

            return JsonResponse({
                "status": "success",
                "programs": list(programs)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetProgramsView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)
        

class GetSpecializationsView(BaseEducationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company")
        program_slug = request.GET.get("program")

        if not company_slug or not program_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            current_company = get_object_or_404(Company, slug=company_slug)
            program = get_object_or_404(Program, slug=program_slug, company=current_company)

            specializations = Specialization.objects.filter(
                company=current_company, program=program
            ).order_by("-created").values("name", "slug")

            return JsonResponse({
                "status": "success",
                "specializations": list(specializations)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or program not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetSpecializationsView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)


class GetCourseView(BaseEducationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company")
        program_slug = request.GET.get("program")

        if not company_slug or not program_slug:
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            courses = Course.objects.filter(
                company__slug = company_slug, program__slug = program_slug
            ).order_by("-created").values("name", "slug")

            return JsonResponse({
                "status": "success",
                "courses": list(courses)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or program not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetCourseView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)
        

class GetCourseDetailsView(BaseEducationCompanyView, View):
    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({
                "status": "failed",
                "error": "Method Not Allowed"
            }, status=403)

        company_slug = request.GET.get("company")
        program_slug = request.GET.get("program")
        specialization_slug = request.GET.get("specialization")

        if not company_slug or (not specialization_slug and not Program):
            return JsonResponse({
                "status": "failed",
                "error": "Missing required parameters"
            }, status=400)

        try:
            filters = {"company__slug": company_slug}

            if program_slug:
                filters["course__program__slug"] = program_slug

            if specialization_slug:
                filters["course__specialization__slug"] = specialization_slug

            course_details = CourseDetail.objects.filter(
                **filters
                ).order_by("-created").values("course__name", "slug")

            return JsonResponse({
                "status": "success",
                "course_details": list(course_details)
            }, status=200)

        except Http404:
            return JsonResponse({
                "status": "failed",
                "error": "Company or specialization not found"
            }, status=404)
        except Exception as e:
            logger.exception(f"Unexpected error in GetCourseDetailView: {e}")
            return JsonResponse({
                "status": "failed",
                "error": "An unexpected error occurred"
            }, status=500)
        

class BaseEducationView(CompanyBaseView):
    model = Company

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company_slug = self.kwargs.get('slug')
        self.company = self.get_company(company_slug)

        context.update({
            "company": self.company,

            "testimonials": Testimonial.objects.filter(company = self.company).order_by("order")[:12],
            "courses": Course.objects.filter(company = self.company).order_by("?")[:12],

            "clients": Client.objects.filter(company = self.company).order_by("?")[:12],
            "programs": Program.objects.filter(company = self.company).order_by("?")[:12],
        })

        return context
        

class HomeView(BaseEducationView, DetailView):
    template_name = "education/home/home.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        

        context.update({
            "education_home_page": True,
            "tags": MetaTag.objects.filter(company = self.company).order_by("?"),                                
            "faqs": Faq.objects.filter(company = self.company).order_by("?")[:5]
        })
        
        return context
    

class CourseDetailView(BaseEducationView, DetailView):
    model = CourseDetail
    template_name = "education/detail/detail.html"
    context_object_name = "detail"
    slug_url_kwarg = 'slug'

    def get_object(self):
        try:
            return get_object_or_404(self.model, course__slug = self.kwargs.get(self.slug_url_kwarg))
        except Http404:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object = self.get_object()

        self.company = self.object.company

        context.update({
            "company": self.company,
            "education_detail_page": True,
            "courses": Course.objects.filter(company = self.company).order_by("?")[:12],
            "faqs": Faq.objects.filter(company = self.company, course = self.object.course).order_by("?")[:5],
            "testimonials": Testimonial.objects.filter(company = self.company).order_by("order")[:12],
            "clients": Client.objects.filter(company = self.company).order_by("?")[:12],
            "programs": Program.objects.filter(company = self.company).order_by("?")[:12],
            "tags": self.object.meta_tags.all().order_by("-created")
        })



        return context