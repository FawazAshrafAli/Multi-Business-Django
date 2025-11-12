from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    CourseApiViewset, EducationCompanyViewSet, CorporatePartnersViewSet, 
    StudentTestimonialViewSet, EnquiryViewSet,
    ProgramViewset, DetailViewSet, InstituteCourseDetailViewSet,
    CompanyCoursesViewSet, SpecializationViewset,
    DetailSliderViewSet, DetailListViewSet
    )

app_name = "course_api" 

router = DefaultRouter()

router.register(r'courses', CourseApiViewset, basename="course")
router.register(r'companies', EducationCompanyViewSet, basename="company")

# router.register(r'enquiry', EnquiryViewSet)
# router.register(r'programs', ProgramViewset)

companies_router = NestedDefaultRouter(router, r'companies', lookup="company")

companies_router.register(r'programs', ProgramViewset, basename="company-program")
companies_router.register(r'specializations', SpecializationViewset, basename="company-specialization")
companies_router.register(r'enquiries', EnquiryViewSet, basename="company-enquiry")
companies_router.register(r'courses', CompanyCoursesViewSet, basename="company-course")
companies_router.register(r'details', DetailViewSet, basename="company-detail")
companies_router.register(r'detail-list', DetailListViewSet, basename="company-detail-list")
companies_router.register(r'slider-details', DetailSliderViewSet, basename="company-slider-detail")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(companies_router.urls)),
    path('corporate_partners/<str:company_slug>/', CorporatePartnersViewSet.as_view({"get":"list"})),
    path('student_testimonials/<str:company_slug>/', StudentTestimonialViewSet.as_view({"get":"list"})),
    path('institute_course_details/<str:company_slug>/', InstituteCourseDetailViewSet.as_view({"get":"list"})),
]
