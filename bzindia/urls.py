"""
URL configuration for bzindia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.views.static import serve
from django.urls import re_path
from django.views.static import serve
from django.views.generic.base import RedirectView

from company.feeds import (
    CompanyFeed, ContactFeed, CompanyFaqFeed, CompanyBlogFeed,
    CompanyBlogDetailFeed, CompanyAboutFeed, CompanyPrivacyPolicyFeed,
    CompanyTermsAndConditionsFeed, CompanyShippingAndDeliveryPolicyFeed,
    CompanyCancellationAndRefundPolicyFeed
    )
    
from base.feeds import (
    DetailFeed, MultipageFeed, ServiceMultipagesFeed, ProductMultipagesFeed,
    CourseMultipagesFeed, RegistrationMultipagesFeed, CompanyServicesFeed,
    CompanyProductsFeed, CompanyCoursesFeed, CompanyRegistrationsFeed,
    MetaTagFeed, HomeFeed, TestimonialFeed,
    )

urlpatterns = [
    path('django_admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('company/', include('company.urls', namespace="company")),    

    path('admin/', include('superadmin.urls', namespace="superadmin")),
    path('authentication/', include('authentication.urls', namespace="authentication")),
    path('locations/', include('locations.urls', namespace="locations")),
    path('customer/', include('customer.urls', namespace="customer")),
    path('product/', include('product.urls', namespace="product")),
    path('directory/', include('directory.urls', namespace="directory")),
    path('service/', include('service.urls', namespace="service")),
    path('education/', include('educational.urls', namespace="education")),
    path('registration/', include('registration.urls', namespace="registration")),
    path('blog/', include('blog.urls', namespace="blog")),
    path('base/', include('base.urls', namespace="base")),

    # api-urls
    path('company_api/', include('company_api.urls', namespace="company_api")),
    path('registration_api/', include('registration_api.urls', namespace="registration_api")),
    path('course_api/', include('course_api.urls', namespace="course_api")),
    path('service_api/', include('service_api.urls', namespace="service_api")),
    path('product_api/', include('product_api.urls', namespace="product_api")),
    path('meta_tag_api/', include('meta_tag_api.urls', namespace="meta_tag_api")),
    path('destination_api/', include('destination_api.urls', namespace="destination_api")),
    path('blog_api/', include('blog_api.urls', namespace="blog_api")),
    path('location_api/', include('location_api.urls', namespace="location_api")),
    path('home_api/', include('home_api.urls', namespace="home_api")),
    path('contact_api/', include('contact_api.urls', namespace="contact_api")),
    path('custom_pages_api/', include('custom_pages_api.urls', namespace="custom_pages_api")),
    path('meta_api/', include('meta_api.urls', namespace="meta_api")),
    path('search_api/', include('search_api.urls', namespace="search_api")),
    path('directory_api/', include('directory_api.urls', namespace="directory_api")),

    path('services/feed/', ServiceMultipagesFeed()),
    path('products/feed/', ProductMultipagesFeed()),
    path('courses/feed/', CourseMultipagesFeed()),
    path('registrations/feed/', RegistrationMultipagesFeed()),

    path('tag/feed/', MetaTagFeed()),
    path('tag/<str:tag_slug>/feed/', MetaTagFeed()),

    path('feed/', HomeFeed()),
    path('comments/feed/', TestimonialFeed()),

    path('<str:company_slug>/feed/', CompanyFeed()),
    path('<str:company_slug>/contact_us/feed/', ContactFeed()),
    path('<str:company_slug>/about_us/feed/', CompanyAboutFeed()),
    path('<str:company_slug>/faqs/feed/', CompanyFaqFeed()),
    path('<str:company_slug>/blog/feed/', CompanyBlogFeed()),    
    path('<str:company_slug>/blog/<str:blog_slug>/feed/', CompanyBlogDetailFeed()),    
    path('<str:type_slug>/<str:company_slug>/<str:slug>/feed/', DetailFeed()),

    path('<str:company_slug>/services/feed/', CompanyServicesFeed()),
    path('<str:company_slug>/products/feed/', CompanyProductsFeed()),
    path('<str:company_slug>/courses/feed/', CompanyCoursesFeed()),
    path('<str:company_slug>/registrations/feed/', CompanyRegistrationsFeed()),

    path('<str:company_slug>/privacy_policy/feed/', CompanyPrivacyPolicyFeed()),
    path('<str:company_slug>/terms_and_conditions/feed/', CompanyTermsAndConditionsFeed()),
    path('<str:company_slug>/shipping_and_delivery_policy/feed/', CompanyShippingAndDeliveryPolicyFeed()),    
    path('<str:company_slug>/cancellation_and_refund_policy/feed/', CompanyCancellationAndRefundPolicyFeed()),        
    

    path('<str:company_slug>/<str:slug>/feed/', ServiceMultipagesFeed()),
    path('<str:company_slug>/<str:slug>/<str:state_slug>/<str:location_slug>/feed/', MultipageFeed()),

]

urlpatterns += [    

    # ✅ Serve the static sitemap index (generated by management command) at /sitemap.xml
    re_path(
        r'^sitemap_index\.xml$',
        serve,
        {
            'path': 'sitemaps/sitemap_index.xml',
            'document_root': os.path.join(settings.BASE_DIR, 'static'),
        },
        name='sitemap-index'
    ),

    re_path(
        r'^sitemap\.xml$',
        RedirectView.as_view(url='/sitemap_index.xml', permanent=True)
    ),

    re_path(
        r'^(?P<path>sitemap-bzindia(-\d+)?\.xml)$',
        serve,
        {
            'document_root': os.path.join(settings.BASE_DIR, 'static', 'sitemaps'),
        },
        name='bzindia-sitemap'
    ),

    re_path(
        r'^(?P<path>sitemap-products(-\d+)?\.xml)$',
        serve,
        {
            'document_root': os.path.join(settings.BASE_DIR, 'static', 'sitemaps'),
        },
        name='product-sitemap'
    ),

    re_path(
        r'^(?P<path>sitemap-registrations(-\d+)?\.xml)$',
        serve,
        {
            'document_root': os.path.join(settings.BASE_DIR, 'static', 'sitemaps'),
        },
        name='registration-sitemap'
    ),

    re_path(
        r'^(?P<path>sitemap-courses(-\d+)?\.xml)$',
        serve,
        {
            'document_root': os.path.join(settings.BASE_DIR, 'static', 'sitemaps'),
        },
        name='course-sitemap'
    ),

    re_path(
        r'^(?P<path>sitemap-services(-\d+)?\.xml)$',
        serve,
        {
            'document_root': os.path.join(settings.BASE_DIR, 'static', 'sitemaps'),
        },
        name='service-sitemap'
    ),

    re_path(
        r'^(?P<path>sitemap-india(-\d+)?\.xml)$',
        serve,
        {
            'document_root': os.path.join(settings.BASE_DIR, 'static', 'sitemaps'),
        },
        name='india-sitemap'
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
