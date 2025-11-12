from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import (
    CompanyApiViewset, CompanyTypeApiViewset, CompanyBlogViewSet,
    CompanyBlogArchivesViewSets, CompanyAboutUsViewSet,
    ContactEnquiryViewSet, CompanyProgramViewSet,
    CompanyClientViewset, CompanyTestimonialViewset,
    CompanyReviewViewset, CompanyBannerViewset, CompanyContactUsViewset,
    MiniCompanyApiViewset, BriefCompanyTypeApiViewset, 
    NavbarCompanyTypeApiViewset, FooterCompanyTypeApiViewset,
    BaseCompanyViewset, InnerPageCompanyApiViewset,
    MinimalCompanyApiViewset, FaqCompanyApiViewset
    )

app_name = "company_api"

router = DefaultRouter()

router.register(r'companies', CompanyApiViewset, basename="company")
router.register(r'minimal-companies', MinimalCompanyApiViewset, basename="minimal-company")
router.register(r'faq-companies', FaqCompanyApiViewset, basename="faq-company")
router.register(r'inner-companies', InnerPageCompanyApiViewset, basename="inner-company")
router.register(r'brief-companies', MiniCompanyApiViewset, basename="brief-company")
router.register(r'base-companies', BaseCompanyViewset, basename="base-company")
router.register(r'company_types', CompanyTypeApiViewset, basename="company_type")
router.register(r'brief-company-types', BriefCompanyTypeApiViewset, basename="brief-company-type")
router.register(r'navbar-company-types', NavbarCompanyTypeApiViewset, basename="navbar-company-type")
# router.register(r'footer-company-types', FooterCompanyTypeApiViewset, basename="footer-company-type")

companies_router = NestedDefaultRouter(router, r'companies', lookup="company")

companies_router.register(r'programs', CompanyProgramViewSet, basename="company-program")

companies_router.register(r'blogs', CompanyBlogViewSet, basename="company-blog")
companies_router.register(r'archives', CompanyBlogArchivesViewSets, basename="company-archive")
companies_router.register(r'about_us', CompanyAboutUsViewSet, basename="company-about")
companies_router.register(r'contact_enquiries', ContactEnquiryViewSet, basename="company-enquiry")

companies_router.register(r'clients', CompanyClientViewset, basename="company-client")
companies_router.register(r'testimonials', CompanyTestimonialViewset, basename="company-testimonial")
companies_router.register(r'reviews', CompanyReviewViewset, basename="company-review")
companies_router.register(r'banners', CompanyBannerViewset, basename="company-banner")
companies_router.register(r'contact-us', CompanyContactUsViewset, basename="company-contact_us")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(companies_router.urls)),
    path("footer-company-types/", FooterCompanyTypeApiViewset.as_view({"get": "list"})),
]
