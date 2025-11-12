from django.urls import path
from .views import (
    HomeView, CompanyListView, AddCompanyView, UpdateCompanyView, DeleteCompanyView,
    CompanyDetailView,
    CompanyTypeListView, AddCompanyTypeView, DeleteCompanyTypeView, UpdateCompanyTypeView,    

    # Product Company

    ListProductView, AddProductView, UpdateProductView, DeleteProductView,
    ListBrandView, AddBrandView, UpdateBrandView, DeleteBrandView,
    ListProductCategoryView, AddProductCategoryView, UpdateProductCategoryView, DeleteProductCategoryView,
    ListProductSubCategoryView, AddProductSubCategoryView, UpdateProductSubCategoryView, DeleteProductSubCategoryView,
    ListProductColorView, AddProductColorView, UpdateProductColorView, DeleteProductColorView,

    AddSizeView, UpdateSizeView, ListSizeView, DeleteSizeView,

    AddProductFaqView, ListProductFaqView, UpdateProductFaqView, DeleteProductFaqView,
    AddProductReviewView, ProductReviewListView, UpdateProductReviewView, DeleteProductReviewView,

    ListProductEnquiryView, DeleteProductEnquiryView,

    AddProductDetailPageView, ProductDetailPageListView, ProductDetailPageView, UpdateProductDetailPageView, DeleteProductDetailPageView,
    DeleteProductMultiPageView,

    AddProductMultiPageView, ProductMultiPageListView, ProductMultiPageDetailView, UpdateProductMultiPageView,

    ProductBannerListView, CreateProductBannerView, UpdateProductBannerView, DeleteProductBannerView,

    # Educational Company
    AddCourseView, CourseListView, RemoveCourseView, UpdateCourseView,
    CourseProgramListView, AddCourseProgramView, RemoveCourseProgramView, UpdateCourseProgramView,
    CourseSpecializationListView, AddCourseSpecializationView, RemoveCourseSpecializationView, UpdateCourseSpecializationView,
    AddCourseDetailView, UpdateCourseDetailView, CourseDetailsListView, CourseDetailView,
    DeleteCourseDetailView,
    AddCourseFaqView, ListCourseFaqView, UpdateCourseFaqView, DeleteCourseFaqView,
    ListCourseEnquiryView, DeleteCourseEnquiryView,

    AddCourseMultiPageView, CourseMultiPageListView, CourseMultiPageDetailView, UpdateCourseMultiPageView,
    DeleteCourseMultiPageView,
    
    EducationBannerListView, CreateEducationBannerView, UpdateEducationBannerView, DeleteEducationBannerView,

    # Service Company
    ListServiceView, AddServiceView, RemoveServiceView, UpdateServiceView,
    ListServiceCategoryView, AddServiceCategoryView, RemoveServiceCategoryView, UpdateServiceCategoryView,
    ListServiceSubCategoryView, AddServiceSubCategoryView, RemoveServiceSubCategoryView, UpdateServiceSubCategoryView,
    AddServiceFaqView, ListServiceFaqView, UpdateServiceFaqView, DeleteServiceFaqView,
    ListServiceEnquiryView, DeleteServiceEnquiryView,

    AddServiceDetailView, ServiceDetailsListView, ServiceDetailView, UpdateServiceDetailView,
    DeleteServiceDetailPageView,

    AddServiceMultiPageView, ServiceMultiPageListView, ServiceMultiPageDetailView, UpdateServiceMultiPageView,
    DeleteServiceMultiPageView,

    ServiceBannerListView, CreateServiceBannerView, UpdateServiceBannerView, DeleteServiceBannerView,

    # Registration Company
    ListRegistrationView, AddRegistrationView, RemoveRegistrationView, UpdateRegistrationView,
    ListRegistrationTypeView, AddRegistrationTypeView, RemoveRegistrationTypeView, UpdateRegistrationTypeView,
    ListRegistrationSubTypeView, AddRegistrationSubTypeView, RemoveRegistrationSubTypeView, UpdateRegistrationSubTypeView,

    AddRegistrationDetailPageView, RegistrationDetailPageListView, RegistrationDetailPageView, UpdateRegistrationDetailPageView,
    DeleteRegistrationDetailPageView,

    AddRegistrationFaqView, ListRegistrationFaqView, UpdateRegistrationFaqView, DeleteRegistrationFaqView,    

    ListRegistrationEnquiryView, DeleteRegistrationEnquiryView,

    AddRegistrationMultiPageView, RegistrationMultiPageListView, RegistrationMultiPageDetailView, UpdateRegistrationMultiPageView,
    DeleteRegistrationMultiPageView,

    RegistrationBannerListView, CreateRegistrationBannerView, UpdateRegistrationBannerView, DeleteRegistrationBannerView,

    # Directory
    BaseDirectoryView,
    ListPostOfficeView, ListBankView, ListCourtView, ListPoliceStationView, ListDestinationView,

    CompanyView,

    SettingsView, UpdatePasswordView, UpdateUserDetailView,

    # Custom pages
    AddCustomPageView, AddAboutUsPageView, AddContactUsPageView, AddFaqPageView,
    AddPrivacyPolicyPageView, AddTermsAndConditionsPageView,
    BaseCustomPageView, ListAboutUsView, ListContactUsView, ListFaqView,
    ListPrivacyPolicyView, ListTermsAndConditionsView, AddShippingAndDeliveryPolicyPageView,
    ListShippingAndDeliveryPolicyView, ListCancellationAndRefundPolicyView,
    AddCancellationAndRefundPolicyPageView,

    UpdateAboutUsPageView, UpdateContactUsPageView, UpdateFaqPageView, 
    UpdatePrivacyPolicyPageView, UpdateTermsAndConditionsPageView,

    DeleteAboutUsPageView, DeleteContactUsPageView, DeleteFaqPageView,
    DeletePrivacyPolicyPageView, DeleteTermsAndConditionPageView,
    DeleteShippingAndDeliveryPolicyPageView, DeleteCancellationAndRefundPolicyPageView,

    # Clients
    AddClientView, ClientListView, UpdateClientView, DeleteClientView,

    UpdateClientSliderHeadingView,

    # Student Testimonials
    AddStudentTestimonialView, StudentTestimonialListView, UpdateStudentTestimonialView, DeleteStudentTestimonialView,

    # General Testimonials
    AddTestimonialView, TestimonialListView, UpdateTestimonialView, DeleteTestimonialView,

    # Blog
    AddBlogView, ListBlogView, UpdateBlogView, DeleteBlogView,
    PublishBlogView, UnPublishBlogView,

    # Meta Tag
    MetaTagListView, AddMetaTagView, UpdateMetaTagView, DeleteMetaTagView,

    # Home Content
    HomeContentView,

    # Functions
    UpdateCheckedServiceMultipageView, UpdateCheckedCourseMultipageView, 
    UpdateCheckedRegistrationMultipageView, UpdateCheckedProductMultipageView
    )

app_name = "superadmin"

urlpatterns = [
    path('', HomeView.as_view(), name="home"),

    path('companies/', CompanyView.as_view(), name="companies"),

    # Company
    path('add_company/', AddCompanyView.as_view(), name="add_company"),
    path('update_company/<str:slug>', UpdateCompanyView.as_view(), name="update_company"),
    path('delete_company/<str:slug>', DeleteCompanyView.as_view(), name="delete_company"),
    path('companies/<str:slug>', CompanyListView.as_view(), name="filtered_companies"),

    path('company/<str:slug>', CompanyDetailView.as_view(), name="company"),

    path('add_company_type/', AddCompanyTypeView.as_view(), name="add_company_type"),
    path('update_company_type/<str:slug>', UpdateCompanyTypeView.as_view(), name="update_company_type"),
    path('company_types/', CompanyTypeListView.as_view(), name="company_types"),
    path('delete_company_type/<str:slug>', DeleteCompanyTypeView.as_view(), name="delete_company_type"),    

    # Product Company
    path('<str:slug>/products', ListProductView.as_view(), name="products"),
    path('<str:slug>/products/add', AddProductView.as_view(), name="add_product"),
    path('<str:slug>/products/<str:product_slug>/update', UpdateProductView.as_view(), name="update_product"),
    path('delete_product/<str:slug>/<str:product_slug>', DeleteProductView.as_view(), name="delete_product"),

    path('<str:slug>/brands', ListBrandView.as_view(), name="brands"),
    path('<str:slug>/brands/add/', AddBrandView.as_view(), name="add_brand"),
    path('<str:slug>/brands/<str:brand_slug>/update/', UpdateBrandView.as_view(), name="update_brand"),
    path('<str:slug>/brands/<str:brand_slug>/delete/', DeleteBrandView.as_view(), name="delete_brand"),

    path('add_category/<str:slug>', AddProductCategoryView.as_view(), name="add_category"),
    path('categories/<str:slug>', ListProductCategoryView.as_view(), name="categories"),
    path('update_category/<str:slug>/<str:category_slug>', UpdateProductCategoryView.as_view(), name="update_category"),
    path('delete_category/<str:slug>/<str:category_slug>', DeleteProductCategoryView.as_view(), name="delete_category"),

    path('add_sub_category/<str:slug>', AddProductSubCategoryView.as_view(), name="add_sub_category"),
    path('sub_categories/<str:slug>', ListProductSubCategoryView.as_view(), name="sub_categories"),
    path('update_sub_category/<str:slug>/<str:sub_category_slug>', UpdateProductSubCategoryView.as_view(), name="update_sub_category"),
    path('delete_sub_category/<str:slug>/<str:sub_category_slug>', DeleteProductSubCategoryView.as_view(), name="delete_sub_category"),

    path('add_size/<str:slug>', AddSizeView.as_view(), name="add_size"),
    path('sizes/<str:slug>', ListSizeView.as_view(), name="sizes"),
    path('update_size/<str:slug>/<str:size_slug>', UpdateSizeView.as_view(), name="update_size"),
    path('delete_size/<str:slug>/<str:size_slug>', DeleteSizeView.as_view(), name="delete_size"),

    path('add_color/<str:slug>', AddProductColorView.as_view(), name="add_color"),
    path('colors/<str:slug>', ListProductColorView.as_view(), name="colors"),
    path('update_color/<str:slug>/<str:color_slug>', UpdateProductColorView.as_view(), name="update_color"),
    path('delete_color/<str:slug>/<str:color_slug>', DeleteProductColorView.as_view(), name="delete_color"),

    path('add_product_faq/<str:slug>', AddProductFaqView.as_view(), name="add_product_faq"),
    path('product_faqs/<str:slug>', ListProductFaqView.as_view(), name="product_faqs"),
    path('update_product_faq/<str:slug>/<str:product_faq_slug>', UpdateProductFaqView.as_view(), name="update_product_faq"),
    path('delete_product_faq/<str:slug>/<str:product_faq_slug>', DeleteProductFaqView.as_view(), name="delete_product_faq"),

    path('add_product_reviews/<str:slug>', AddProductReviewView.as_view(), name="add_product_reviews"),
    path('product_reviews/<str:slug>', ProductReviewListView.as_view(), name="product_reviews"),
    path('update_product_review/<str:slug>/<str:product_review_slug>', UpdateProductReviewView.as_view(), name="update_product_review"),
    path('delete_product_review/<str:slug>/<str:product_review_slug>', DeleteProductReviewView.as_view(), name="delete_product_review"),

    path('product_enquiries/<str:slug>', ListProductEnquiryView.as_view(), name="product_enquiries"),
    path('delete_product_enquiry/<str:slug>/<str:enquiry_slug>/', DeleteProductEnquiryView.as_view(), name="delete_product_enquiry"),

    path('add_product_detail_page/<str:slug>', AddProductDetailPageView.as_view(), name="add_product_detail_page"),
    path('update_product_detail_page/<str:slug>/<str:product_detail_slug>', UpdateProductDetailPageView.as_view(), name="update_product_detail_page"),
    path('product_detail_pages/<str:slug>', ProductDetailPageListView.as_view(), name="product_detail_pages"),
    path('product_detail_page/<str:slug>/<str:product_detail_slug>', ProductDetailPageView.as_view(), name="product_detail_page"),
    path('delete_product_detail_page/<str:slug>/<str:detail_page_slug>', DeleteProductDetailPageView.as_view(), name="delete_product_detail_page"),

    path('add_product_multipage/<str:slug>', AddProductMultiPageView.as_view(), name="add_product_multipage"),
    path('product_multipages/<str:slug>', ProductMultiPageListView.as_view(), name="product_multipages"),
    path('update_product_multipage/<str:slug>/<str:multipage_slug>', UpdateProductMultiPageView.as_view(), name="update_product_multipage"),
    path('product_multipage/<str:slug>/<str:multipage_slug>', ProductMultiPageDetailView.as_view(), name="product_multipage"),
    path('delete_product_multipage/<str:slug>/<str:multipage_slug>', DeleteProductMultiPageView.as_view(), name="delete_product_multipage"),

    path('add_product_banner/<str:slug>', CreateProductBannerView.as_view(), name="add_product_banner"),
    path('product_banners/<str:slug>', ProductBannerListView.as_view(), name="product_banners"),
    path('update_product_banner/<str:slug>/<str:banner_slug>/', UpdateProductBannerView.as_view(), name="update_product_banner"),
    path('delete_product_banner/<str:slug>/<str:banner_slug>/', DeleteProductBannerView.as_view(), name="delete_product_banner"),

    # Education Company
    path('add_course/<str:slug>', AddCourseView.as_view(), name="add_course"),
    path('courses/<str:slug>', CourseListView.as_view(), name="courses"),
    path('remove_course/<str:slug>/<str:course_slug>/', RemoveCourseView.as_view(), name="remove_course"),
    path('update_course/<str:slug>/<str:course_slug>/', UpdateCourseView.as_view(), name="update_course"),

    path('course_enquiries/<str:slug>', ListCourseEnquiryView.as_view(), name="course_enquiries"),
    path('delete_course_enquiry/<str:slug>/<str:enquiry_slug>/', DeleteCourseEnquiryView.as_view(), name="delete_course_enquiry"),

    path('add_education_banner/<str:slug>', CreateEducationBannerView.as_view(), name="add_education_banner"),
    path('education_banners/<str:slug>', EducationBannerListView.as_view(), name="education_banners"),
    path('update_education_banner/<str:slug>/<str:banner_slug>/', UpdateEducationBannerView.as_view(), name="update_education_banner"),
    path('delete_education_banner/<str:slug>/<str:banner_slug>/', DeleteEducationBannerView.as_view(), name="delete_education_banner"),

    path('add_course_details/<str:slug>', AddCourseDetailView.as_view(), name="add_course_details"),
    path('update_course_details/<str:slug>/<str:course_detail_slug>', UpdateCourseDetailView.as_view(), name="update_course_details"),
    path('course_details/<str:slug>', CourseDetailsListView.as_view(), name="course_details"),
    path('course_detail/<str:slug>/<str:course_slug>', CourseDetailView.as_view(), name="course_detail"),
    path('delete_course_detail/<str:slug>/<str:course_detail_slug>', DeleteCourseDetailView.as_view(), name="delete_course_detail"),

    path('add_course_faq/<str:slug>', AddCourseFaqView.as_view(), name="add_course_faq"),
    path('course_faqs/<str:slug>', ListCourseFaqView.as_view(), name="course_faqs"),
    path('update_course_faq/<str:slug>/<str:course_faq_slug>', UpdateCourseFaqView.as_view(), name="update_course_faq"),
    path('delete_course_faq/<str:slug>/<str:course_faq_slug>', DeleteCourseFaqView.as_view(), name="delete_course_faq"),

    path('course_programs/<str:slug>', CourseProgramListView.as_view(), name="course_programs"),
    path('add_course_program/<str:slug>', AddCourseProgramView.as_view(), name="add_course_program"),
    path('remove_course_program/<str:slug>/<str:program_slug>/', RemoveCourseProgramView.as_view(), name="remove_course_program"),
    path('update_course_program/<str:slug>/<str:program_slug>/', UpdateCourseProgramView.as_view(), name="update_course_program"),

    path('course_specializations/<str:slug>', CourseSpecializationListView.as_view(), name="course_specializations"),
    path('add_course_specialization/<str:slug>', AddCourseSpecializationView.as_view(), name="add_course_specialization"),
    path('remove_course_specialization/<str:slug>/<str:specialization_slug>/', RemoveCourseSpecializationView.as_view(), name="remove_course_specialization"),
    path('update_course_specialization/<str:slug>/<str:specialization_slug>/', UpdateCourseSpecializationView.as_view(), name="update_course_specialization"),

    path('<str:slug>/course_multipages/', CourseMultiPageListView.as_view(), name="course_multipages"),
    path('<str:slug>/course_multipages/add', AddCourseMultiPageView.as_view(), name="add_course_multipage"),
    path('<str:slug>/course_multipages/<str:multipage_slug>', CourseMultiPageDetailView.as_view(), name="course_multipage"),
    path('<str:slug>/course_multipages/<str:multipage_slug>/update', UpdateCourseMultiPageView.as_view(), name="update_course_multipage"),
    path('<str:slug>/course_multipages/<str:multipage_slug>/delete', DeleteCourseMultiPageView.as_view(), name="delete_course_multipage"),

    # Service Company
    path('companies/services/<str:slug>', ListServiceView.as_view(), name="services"),
    path('companies/<str:slug>/add_service', AddServiceView.as_view(), name="add_service"),
    path('remove_service/<str:slug>/<str:category_slug>/', RemoveServiceView.as_view(), name="remove_service"),
    path('update_service/<str:slug>/<str:service_slug>/', UpdateServiceView.as_view(), name="update_service"),
    
    path('companies/service_categories/<str:slug>', ListServiceCategoryView.as_view(), name="service_categories"),
    path('companies/add_service_category/<str:slug>', AddServiceCategoryView.as_view(), name="add_service_category"),
    path('remove_service_category/<str:slug>/<str:category_slug>/', RemoveServiceCategoryView.as_view(), name="remove_service_category"),
    path('update_service_category/<str:slug>/<str:category_slug>/', UpdateServiceCategoryView.as_view(), name="update_service_category"),

    path('companies/service_sub_categories/<str:slug>', ListServiceSubCategoryView.as_view(), name="service_sub_categories"),
    path('companies/add_service_sub_category/<str:slug>', AddServiceSubCategoryView.as_view(), name="add_service_sub_category"),
    path('remove_service_sub_category/<str:slug>/<str:sub_category_slug>/', RemoveServiceSubCategoryView.as_view(), name="remove_service_sub_category"),
    path('update_service_sub_category/<str:slug>/<str:sub_category_slug>/', UpdateServiceSubCategoryView.as_view(), name="update_service_sub_category"),

    path('add_service_faq/<str:slug>', AddServiceFaqView.as_view(), name="add_service_faq"),
    path('service_faqs/<str:slug>', ListServiceFaqView.as_view(), name="service_faqs"),
    path('update_service_faq/<str:slug>/<str:service_faq_slug>', UpdateServiceFaqView.as_view(), name="update_service_faq"),
    path('delete_service_faq/<str:slug>/<str:service_faq_slug>', DeleteServiceFaqView.as_view(), name="delete_service_faq"),

    path('service_enquiries/<str:slug>', ListServiceEnquiryView.as_view(), name="service_enquiries"),
    path('delete_service_enquiry/<str:slug>/<str:enquiry_slug>/', DeleteServiceEnquiryView.as_view(), name="delete_service_enquiry"),

    path('add_service_details/<str:slug>', AddServiceDetailView.as_view(), name="add_service_details"),
    path('service_details/<str:slug>', ServiceDetailsListView.as_view(), name="service_details"),
    path('service_detail/<str:slug>/<str:detail_page_slug>', ServiceDetailView.as_view(), name="service_detail"),
    path('update_service_details/<str:slug>/<str:detail_page_slug>', UpdateServiceDetailView.as_view(), name="update_service_details"),
    path('delete_service_detail_page/<str:slug>/<str:detail_page_slug>', DeleteServiceDetailPageView.as_view(), name="delete_service_detail_page"),

    path('<str:slug>/service_multipages', ServiceMultiPageListView.as_view(), name="service_multipages"),
    path('<str:slug>/service_multipages/add', AddServiceMultiPageView.as_view(), name="add_service_multipage"),
    path('<str:slug>/service_multipages/<str:multipage_slug>', ServiceMultiPageDetailView.as_view(), name="service_multipage"),
    path('<str:slug>/service_multipages/<str:multipage_slug>/update', UpdateServiceMultiPageView.as_view(), name="update_service_multipage"),
    path('<str:slug>/service_multipages/<str:multipage_slug>/delete', DeleteServiceMultiPageView.as_view(), name="delete_service_multipage"),

    path('add_service_banner/<str:slug>', CreateServiceBannerView.as_view(), name="add_service_banner"),
    path('service_banners/<str:slug>', ServiceBannerListView.as_view(), name="service_banners"),
    path('update_service_banner/<str:slug>/<str:banner_slug>/', UpdateServiceBannerView.as_view(), name="update_service_banner"),
    path('delete_service_banner/<str:slug>/<str:banner_slug>/', DeleteServiceBannerView.as_view(), name="delete_service_banner"),

    # Registration Company
    path('companies/registrations/<str:slug>', ListRegistrationView.as_view(), name="registrations"),
    path('companies/add_registration/<str:slug>', AddRegistrationView.as_view(), name="add_registration"),
    path('companies/remove_registration/<str:slug>/<str:registration_slug>/', RemoveRegistrationView.as_view(), name="remove_registration"),
    path('update_registration/<str:slug>/<str:registration_slug>/', UpdateRegistrationView.as_view(), name="update_registration"),

    path('companies/registration_types/<str:slug>', ListRegistrationTypeView.as_view(), name="registration_types"),
    path('companies/add_registration_type/<str:slug>', AddRegistrationTypeView.as_view(), name="add_registration_type"),
    path('companies/remove_registration_type/<str:slug>/<str:registration_type_slug>/', RemoveRegistrationTypeView.as_view(), name="remove_registration_type"),
    path('update_registration_type/<str:slug>/<str:registration_type_slug>/', UpdateRegistrationTypeView.as_view(), name="update_registration_type"),

    path('companies/registration_sub_types/<str:slug>', ListRegistrationSubTypeView.as_view(), name="registration_sub_types"),
    path('companies/add_registration_sub_types/<str:slug>', AddRegistrationSubTypeView.as_view(), name="add_registration_sub_types"),
    path('companies/remove_registration_sub_type/<str:slug>/<str:registration_sub_type_slug>/', RemoveRegistrationSubTypeView.as_view(), name="remove_registration_sub_type"),
    path('update_registration_sub_type/<str:slug>/<str:registration_sub_type_slug>/', UpdateRegistrationSubTypeView.as_view(), name="update_registration_sub_type"),

    path('add_registration_faq/<str:slug>', AddRegistrationFaqView.as_view(), name="add_registration_faq"),
    path('registration_faqs/<str:slug>', ListRegistrationFaqView.as_view(), name="registration_faqs"),
    path('update_registration_faq/<str:slug>/<str:registration_faq_slug>', UpdateRegistrationFaqView.as_view(), name="update_registration_faq"),
    path('delete_registration_faq/<str:slug>/<str:registration_faq_slug>', DeleteRegistrationFaqView.as_view(), name="delete_registration_faq"),

    path('registration_enquiries/<str:slug>', ListRegistrationEnquiryView.as_view(), name="registration_enquiries"),
    path('delete_registration_enquiry/<str:slug>/<str:enquiry_slug>/', DeleteRegistrationEnquiryView.as_view(), name="delete_registration_enquiry"),

    path('add_registration_detail_page/<str:slug>', AddRegistrationDetailPageView.as_view(), name="add_registration_detail_page"),
    path('registration_detail_pages/<str:slug>', RegistrationDetailPageListView.as_view(), name="registration_detail_pages"),
    path('registration_detail_page/<str:slug>/<str:detail_page_slug>', RegistrationDetailPageView.as_view(), name="registration_detail_page"),
    path('update_registration_detail_page/<str:slug>/<str:detail_page_slug>', UpdateRegistrationDetailPageView.as_view(), name="update_registration_detail_page"),
    path('delete_registration_detail_page/<str:slug>/<str:detail_page_slug>', DeleteRegistrationDetailPageView.as_view(), name="delete_registration_detail_page"),

    path('add_registration_multipage/<str:slug>', AddRegistrationMultiPageView.as_view(), name="add_registration_multipage"),
    path('update_registration_multipage/<str:slug>/<str:multipage_slug>', UpdateRegistrationMultiPageView.as_view(), name="update_registration_multipage"),
    path('registration_multipages/<str:slug>', RegistrationMultiPageListView.as_view(), name="registration_multipages"),
    path('registration_multipage/<str:slug>/<str:multipage_slug>', RegistrationMultiPageDetailView.as_view(), name="registration_multipage"),
    path('delete_registration_multipage/<str:slug>/<str:multipage_slug>', DeleteRegistrationMultiPageView.as_view(), name="delete_registration_multipage"),

    path('add_registration_banner/<str:slug>', CreateRegistrationBannerView.as_view(), name="add_registration_banner"),
    path('registration_banners/<str:slug>', RegistrationBannerListView.as_view(), name="registration_banners"),
    path('update_registration_banner/<str:slug>/<str:banner_slug>/', UpdateRegistrationBannerView.as_view(), name="update_registration_banner"),
    path('delete_registration_banner/<str:slug>/<str:banner_slug>/', DeleteRegistrationBannerView.as_view(), name="delete_registration_banner"),

    # Directory

    path('directories/', BaseDirectoryView.as_view(), name="directories"),

    path('directories/post_offices/', ListPostOfficeView.as_view(), name="post_offices"),

    path('directories/banks/', ListBankView.as_view(), name="banks"),

    path('directories/courts/', ListCourtView.as_view(), name="courts"),

    path('directories/police_stations/', ListPoliceStationView.as_view(), name="police_stations"),

    path('directories/destinations/', ListDestinationView.as_view(), name="destinations"),

    # Settings
    path('settings/', SettingsView.as_view(), name="settings"),
    path('update_password/', UpdatePasswordView.as_view(), name="update_password"),
    path('update_user_details/', UpdateUserDetailView.as_view(), name="update_user_details"),
    
    path('add_custom_page/', AddCustomPageView.as_view(), name="add_custom_page"),    
    path('custom_pages/', BaseCustomPageView.as_view(), name="custom_pages"),

    path('add_about_us/', AddAboutUsPageView.as_view(), name="add_about_us"),
    path('about_us/', ListAboutUsView.as_view(), name="about_us"),
    path('delete_about_us/<str:about_us_slug>', DeleteAboutUsPageView.as_view(), name="delete_about_us"),
    path('update_about_us/<str:about_us_slug>', UpdateAboutUsPageView.as_view(), name="update_about_us"),

    path('add_contact_us/', AddContactUsPageView.as_view(), name="add_contact_us"),
    path('contact_us/', ListContactUsView.as_view(), name="contact_us"),
    path('delete_contact_us/<str:contact_us_slug>', DeleteContactUsPageView.as_view(), name="delete_contact_us"),
    path('update_contact_us/<str:contact_us_slug>', UpdateContactUsPageView.as_view(), name="update_contact_us"),

    path('add_faq/', AddFaqPageView.as_view(), name="add_faq"),
    path('faq/', ListFaqView.as_view(), name="faq"),
    path('delete_faq/<str:faq_slug>', DeleteFaqPageView.as_view(), name="delete_faq"),
    path('update_faq/<str:faq_slug>', UpdateFaqPageView.as_view(), name="update_faq"),

    path('add_privacy_policy/', AddPrivacyPolicyPageView.as_view(), name="add_privacy_policy"),
    path('privacy_policies/', ListPrivacyPolicyView.as_view(), name="privacy_policies"),
    path('delete_privacy_policy/<str:privacy_policy_slug>', DeletePrivacyPolicyPageView.as_view(), name="delete_privacy_policy"),
    path('update_privacy_policy/<str:privacy_policy_slug>', UpdatePrivacyPolicyPageView.as_view(), name="update_privacy_policy"),

    path('add_terms_and_conditions/', AddTermsAndConditionsPageView.as_view(), name="add_terms_and_conditions"),
    path('terms_and_conditions/', ListTermsAndConditionsView.as_view(), name="terms_and_conditions"),
    path('delete_terms_and_condition/<str:terms_and_condition_slug>', DeleteTermsAndConditionPageView.as_view(), name="delete_terms_and_condition"),
    path('update_terms_and_condition/<str:terms_and_condition_slug>', UpdateTermsAndConditionsPageView.as_view(), name="update_terms_and_condition"),

    path('add_shipping_and_delivery_policy/', AddShippingAndDeliveryPolicyPageView.as_view(), name="add_shipping_and_delivery_policy"),
    path('shipping_and_delivery_policies/', ListShippingAndDeliveryPolicyView.as_view(), name="shipping_and_delivery_policies"),
    path('delete_shipping_and_delivery_policy/<str:shipping_and_delivery_policy_slug>', DeleteShippingAndDeliveryPolicyPageView.as_view(), name="delete_shipping_and_delivery_policy"),

    path('add_cancellation_and_refund_policy/', AddCancellationAndRefundPolicyPageView.as_view(), name="add_cancellation_and_refund_policy"),
    path('cancellation_and_refund_policies/', ListCancellationAndRefundPolicyView.as_view(), name="cancellation_and_refund_policies"),
    path('delete_cancellation_and_refund_policy/<str:cancellation_and_refund_policy_slug>', DeleteCancellationAndRefundPolicyPageView.as_view(), name="delete_cancellation_and_refund_policy"),     

    # Clients
    path('add_client/<str:slug>', AddClientView.as_view(), name="add_client"),
    path('clients/<str:slug>', ClientListView.as_view(), name="clients"),
    path('update_client/<str:slug>/<str:client_slug>', UpdateClientView.as_view(), name="update_client"),
    path('delete_client/<str:slug>/<str:client_slug>', DeleteClientView.as_view(), name="delete_client"),

    path('update_client_slider_heading/<str:slug>', UpdateClientSliderHeadingView.as_view(), name="update_client_slider_heading"),

    # StudentTestimonials
    path('add_student_testimonial/<str:slug>', AddStudentTestimonialView.as_view(), name="add_student_testimonial"),
    path('student_testimonials/<str:slug>', StudentTestimonialListView.as_view(), name="student_testimonials"),
    path('update_student_testimonial/<str:slug>/<str:testimonial_slug>', UpdateStudentTestimonialView.as_view(), name="update_student_testimonial"),
    path('delete_student_testimonial/<str:slug>/<str:testimonial_slug>', DeleteStudentTestimonialView.as_view(), name="delete_student_testimonial"),

    # General Testimonials
    path('add_testimonial/<str:slug>', AddTestimonialView.as_view(), name="add_testimonial"),
    path('testimonials/<str:slug>', TestimonialListView.as_view(), name="testimonials"),
    path('update_testimonial/<str:slug>/<str:testimonial_slug>', UpdateTestimonialView.as_view(), name="update_testimonial"),
    path('delete_testimonial/<str:slug>/<str:testimonial_slug>', DeleteTestimonialView.as_view(), name="delete_testimonial"),

    # Blog
    path('add_blogs/', AddBlogView.as_view(), name="add_blogs"),
    path('blogs/', ListBlogView.as_view(), name="blogs"),
    path('update_blog/<str:slug>', UpdateBlogView.as_view(), name="update_blog"),
    path('delete_blog/<str:slug>', DeleteBlogView.as_view(), name="delete_blog"),

    path('publish_blog/<str:slug>', PublishBlogView.as_view(), name="publish_blog"),
    path('unpublish_blog/<str:slug>', UnPublishBlogView.as_view(), name="unpublish_blog"),

    # Meta Tag
    path('meta_tags/', MetaTagListView.as_view(), name="meta_tags"),
    path('add_meta_tag/', AddMetaTagView.as_view(), name="add_meta_tag"),
    path('update_meta_tag/<str:slug>', UpdateMetaTagView.as_view(), name="update_meta_tag"),
    path('delete_meta_tag/<str:slug>', DeleteMetaTagView.as_view(), name="delete_meta_tag"),

    # Home
    path('home_main_content/', HomeContentView.as_view(), name="home_main_content"),

    # Functions
    path('update_checked_service_multipage/', UpdateCheckedServiceMultipageView.as_view(), name="update_checked_service_multipage"),
    path('update_checked_course_multipage/', UpdateCheckedCourseMultipageView.as_view(), name="update_checked_course_multipage"),
    path('update_checked_registration_multipage/', UpdateCheckedRegistrationMultipageView.as_view(), name="update_checked_registration_multipage"),
    path('update_checked_product_multipage/', UpdateCheckedProductMultipageView.as_view(), name="update_checked_product_multipage"),
]
