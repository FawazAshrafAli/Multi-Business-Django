from django.urls import path

from .views import (CustomerHomeView, 
                    AddProductCategoryView, DeleteProductCategoryView, UpdateProductCategoryView, ListProductCategoryView,
                    AddProductSubCategoryView, ListProductSubCategoryView, UpdateProductSubCategoryView, DeleteProductSubCategoryView,
                    AddBrandView, DeleteBrandView, UpdateBrandView, ListBrandView, 
                    AddSizeView, DeleteSizeView, UpdateSizeView, ListSizeView,
                    AddColorView, DeleteColorView, UpdateColorView, ListColorView, 
                    AddProductView, DeleteProductView, UpdateProductView, ListProductView,
                    get_sub_categories_and_sizes,
                    
                    # Service Company
                    ServiceListView, DeleteServiceView, AddServiceView, UpdateServiceView,
                    AddServiceCategoryView, ListServiceCategoryView, UpdateServiceCategoryView, DeleteServiceCategoryView,
                    AddServiceSubCategoryView, ListServiceSubCategoryView, UpdateServiceSubCategoryView, DeleteServiceSubCategoryView,
                    ListServiceFaqView, AddServiceFaqView, DeleteServiceFaqView, UpdateServiceFaqView,
                    ListServiceEnquiryView, DeleteServiceEnquiryView,

                    # Registration Company
                    AddRegistrationView, ListRegistrationView, UpdateRegistrationView, DeleteRegistrationView,
                    AddRegistrationTypeView, ListRegistrationTypeView, UpdateRegistrationTypeView, DeleteRegistrationTypeView,
                    AddRegistrationSubTypeView, ListRegistrationSubTypeView, UpdateRegistrationSubTypeView, DeleteRegistrationSubTypeView,
                    AddRegistrationFaqView, ListRegistrationFaqView, UpdateRegistrationFaqView, DeleteRegistrationFaqView,
                    ListRegistrationEnquiryView, DeleteRegistrationEnquiryView,

                    # Education Company
                    CourseListView, AddCourseView, UpdateCourseView, DeleteCourseView,
                    ListCourseProgramView, ListCourseSpecializationView,
                    AddCourseFaqView, ListCourseFaqView, UpdateCourseFaqView, DeleteCourseFaqView,
                    ListCourseEnquiryView, DeleteCourseEnquiryView,
                    AddStudentTestimonialView, StudentTestimonialListView, UpdateStudentTestimonialView, DeleteStudentTestimonialView,

                    # Clients
                    AddClientView, ClientListView, UpdateClientView, DeleteClientView,

                    # General Testimonials
                    AddTestimonialView, TestimonialListView, UpdateTestimonialView, DeleteTestimonialView,
                    )

app_name = "customer"

urlpatterns = [
    path('', CustomerHomeView.as_view(), name="home"),

    # Product Company
    path('add_product_category/', AddProductCategoryView.as_view(), name="add_product_category"),
    path('product_categories/', ListProductCategoryView.as_view(), name="product_categories"),
    path('update_product_category/<str:slug>', UpdateProductCategoryView.as_view(), name="update_product_category"),
    path('delete_product_category/<str:slug>', DeleteProductCategoryView.as_view(), name="delete_product_category"),

    path('add_product_sub_category/', AddProductSubCategoryView.as_view(), name="add_product_sub_category"),
    path('product_sub_categories/', ListProductSubCategoryView.as_view(), name="product_sub_categories"),
    path('update_product_sub_category/<str:slug>', UpdateProductSubCategoryView.as_view(), name="update_product_sub_category"),
    path('delete_product_sub_category/<str:slug>', DeleteProductSubCategoryView.as_view(), name="delete_product_sub_category"),
    path('get_product_sub_categories/', get_sub_categories_and_sizes, name="get_product_sub_categories"),

    path('add_brand/', AddBrandView.as_view(), name="add_brand"),
    path('brands/', ListBrandView.as_view(), name="brands"),
    path('update_brand/<str:slug>', UpdateBrandView.as_view(), name="update_brand"),
    path('delete_brand/<str:slug>', DeleteBrandView.as_view(), name="delete_brand"),

    path('add_size/', AddSizeView.as_view(), name="add_size"),
    path('sizes/', ListSizeView.as_view(), name="sizes"),
    path('update_size/<str:slug>', UpdateSizeView.as_view(), name="update_size"),
    path('delete_size/<str:slug>', DeleteSizeView.as_view(), name="delete_size"),

    path('add_color/', AddColorView.as_view(), name="add_color"),
    path('colors/', ListColorView.as_view(), name="colors"),
    path('update_color/<str:slug>', UpdateColorView.as_view(), name="update_color"),
    path('delete_color/<str:slug>', DeleteColorView.as_view(), name="delete_color"),

    path('add_product/', AddProductView.as_view(), name="add_product"),
    path('products/', ListProductView.as_view(), name="products"),
    path('update_product/<str:slug>', UpdateProductView.as_view(), name="update_product"),
    path('delete_product/<str:slug>', DeleteProductView.as_view(), name="delete_product"),

    path('get_sub_categories_and_sizes/', get_sub_categories_and_sizes, name="get_sub_categories_and_sizes"),


    # Service Company
    path('services/', ServiceListView.as_view(), name="services"),
    path('add_services/', AddServiceView.as_view(), name="add_services"),
    path('delete_service/<str:slug>', DeleteServiceView.as_view(), name="delete_service"),
    path('update_service/<str:slug>', UpdateServiceView.as_view(), name="update_service"),

    path('service_categories/', ListServiceCategoryView.as_view(), name="service_categories"),
    path('add_service_categories/', AddServiceCategoryView.as_view(), name="add_service_categories"),
    path('delete_service_category/<str:slug>', DeleteServiceCategoryView.as_view(), name="delete_service_category"),
    path('update_service_category/<str:slug>', UpdateServiceCategoryView.as_view(), name="update_service_category"),

    path('service_sub_categories/', ListServiceSubCategoryView.as_view(), name="service_sub_categories"),
    path('add_service_sub_categories/', AddServiceSubCategoryView.as_view(), name="add_service_sub_categories"),
    path('delete_service_sub_category/<str:slug>', DeleteServiceSubCategoryView.as_view(), name="delete_service_sub_category"),
    path('update_service_sub_category/<str:slug>', UpdateServiceSubCategoryView.as_view(), name="update_service_sub_category"),

    path('service_faqs/', ListServiceFaqView.as_view(), name="service_faqs"),
    path('add_service_faqs/', AddServiceFaqView.as_view(), name="add_service_faqs"),
    path('delete_service_faq/<str:slug>', DeleteServiceFaqView.as_view(), name="delete_service_faq"),
    path('update_service_faq/<str:slug>', UpdateServiceFaqView.as_view(), name="update_service_faq"),

    path('service_enquiries/', ListServiceEnquiryView.as_view(), name="service_enquiries"),
    path('delete_service_enquiry/<str:slug>', DeleteServiceEnquiryView.as_view(), name="delete_service_enquiry"),

    # Registration Company
    path('add_registrations/', AddRegistrationView.as_view(), name="add_registrations"),
    path('registrations/', ListRegistrationView.as_view(), name="registrations"),
    path('update_registration/<str:slug>', UpdateRegistrationView.as_view(), name="update_registration"),
    path('delete_registration/<str:slug>', DeleteRegistrationView.as_view(), name="delete_registration"),

    path('add_registration_types/', AddRegistrationTypeView.as_view(), name="add_registration_types"),
    path('registration_types/', ListRegistrationTypeView.as_view(), name="registration_types"),
    path('update_registration_type/<str:slug>', UpdateRegistrationTypeView.as_view(), name="update_registration_type"),
    path('delete_registration_type/<str:slug>', DeleteRegistrationTypeView.as_view(), name="delete_registration_type"),

    path('add_registration_sub_types/', AddRegistrationSubTypeView.as_view(), name="add_registration_sub_types"),
    path('registration_sub_types/', ListRegistrationSubTypeView.as_view(), name="registration_sub_types"),
    path('update_registration_sub_type/<str:slug>', UpdateRegistrationSubTypeView.as_view(), name="update_registration_sub_type"),
    path('delete_registration_sub_type/<str:slug>', DeleteRegistrationSubTypeView.as_view(), name="delete_registration_sub_type"),

    path('add_registration_faqs/', AddRegistrationFaqView.as_view(), name="add_registration_faqs"),
    path('registration_faqs/', ListRegistrationFaqView.as_view(), name="registration_faqs"),
    path('update_registration_faq/<str:slug>', UpdateRegistrationFaqView.as_view(), name="update_registration_faq"),
    path('delete_registration_faq/<str:slug>', DeleteRegistrationFaqView.as_view(), name="delete_registration_faq"),

    path('registration_enquiries/', ListRegistrationEnquiryView.as_view(), name="registration_enquiries"),
    path('delete_registration_enquiry/<str:slug>', DeleteRegistrationEnquiryView.as_view(), name="delete_registration_enquiry"),

    # Education Company
    path('add_courses/', AddCourseView.as_view(), name="add_courses"),
    path('courses/', CourseListView.as_view(), name="courses"),
    path('update_course/<str:slug>', UpdateCourseView.as_view(), name="update_course"),
    path('delete_course/<str:slug>', DeleteCourseView.as_view(), name="delete_course"),

    path('course_programs/', ListCourseProgramView.as_view(), name="course_programs"),
    path('course_specializations/', ListCourseSpecializationView.as_view(), name="course_specializations"),

    path('add_course_faqs/', AddCourseFaqView.as_view(), name="add_course_faqs"),
    path('course_faqs/', ListCourseFaqView.as_view(), name="course_faqs"),
    path('update_course_faq/<str:slug>', UpdateCourseFaqView.as_view(), name="update_course_faq"),
    path('delete_course_faq/<str:slug>', DeleteCourseFaqView.as_view(), name="delete_course_faq"),

    path('course_enquiries/', ListCourseEnquiryView.as_view(), name="course_enquiries"),
    path('delete_course_enquiry/<str:slug>', DeleteCourseEnquiryView.as_view(), name="delete_course_enquiry"),

    path('add_student_testimonials/', AddStudentTestimonialView.as_view(), name="add_student_testimonials"),
    path('student_testimonials/', StudentTestimonialListView.as_view(), name="student_testimonials"),
    path('update_student_testimonial/<str:slug>', UpdateStudentTestimonialView.as_view(), name="update_student_testimonial"),
    path('delete_student_testimonial/<str:slug>', DeleteStudentTestimonialView.as_view(), name="delete_student_testimonial"),

    # Clients
    path('clients/', ClientListView.as_view(), name="clients"),
    path('add_clients/', AddClientView.as_view(), name="add_clients"),
    path('update_client/<str:slug>', UpdateClientView.as_view(), name="update_client"),
    path('delete_client/<str:slug>', DeleteClientView.as_view(), name="delete_client"),

    # General Testimonial
    path('testimonials/', TestimonialListView.as_view(), name="testimonials"),
    path('add_testimonials/', AddTestimonialView.as_view(), name="add_testimonials"),
    path('update_testimonial/<str:slug>', UpdateTestimonialView.as_view(), name="update_testimonial"),
    path('delete_testimonial/<str:slug>', DeleteTestimonialView.as_view(), name="delete_testimonial"),
]
