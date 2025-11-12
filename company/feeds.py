from django.http import HttpResponse
from django.contrib.syndication.views import Feed
from .models import Company
from utility.custom_feed import ContentEncodedFeed
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from product.models import ProductDetailPage
from service.models import ServiceDetail
from registration.models import RegistrationDetailPage
from educational.models import CourseDetail
from blog.models import Blog

from django.utils.html import escape
from django.utils.text import Truncator
from django.utils.html import strip_tags

from company.models import Company
from custom_pages.models import (
    ContactUs, FAQ, AboutUs, PrivacyPolicy, TermsAndCondition, 
    ShippingAndDeliveryPolicy, CancellationAndRefundPolicy
    )

class CompanyFeed(Feed):
    feed_type = ContentEncodedFeed
    title = "BZ India - Find the top companies in India"
    description = "BZ India blog feed updates."

    def get_object(self, request, company_slug):
        return get_object_or_404(Company, slug = company_slug)

    def title(self, obj):
        return obj.meta_title if obj.meta_title else obj.name

    def link(self, obj):
        return f"/{obj.slug}/feed/"

    def description(self, obj):
        return obj.meta_description if obj.meta_description else obj.name

    def items(self, obj):
        if (obj.type.name == "Service"):
            return ServiceDetail.objects.filter(company=obj).order_by('-created')[:15]
        elif (obj.type.name == "Education"):
            return CourseDetail.objects.filter(company=obj).order_by('-created')[:15]
        elif (obj.type.name == "Registration"):
            return RegistrationDetailPage.objects.filter(company=obj).order_by('-created')[:15]
        elif (obj.type.name == "Product"):
            return ProductDetailPage.objects.filter(company=obj).order_by('-created')[:15]
        
        return []

    def item_title(self, item):
        if (item.company.type.name == "Service"):
            return item.service.name
        elif (item.company.type.name == "Education"):
            return item.course.name
        elif (item.company.type.name == "Registration"):
            return item.registration_sub_type.name
        elif (item.company.type.name == "Product"):
            return item.product.name

        return ""

    def item_description(self, item):
        return item.meta_description or ""

    def item_link(self, item):
        return f"/{slugify(item.company.type.name)}/{item.company.slug}/{item.slug}/"

    def item_guid(self, item):
        return f"{item.pk}-{item.slug}"

    def item_pubdate(self, item):
        return item.updated or item.created

    def item_author_name(self, item):
        return item.company.name if item.company else "BZ India"

    def item_enclosure_url(self, item):
        if (item.company.type.name == "Service"):
            return item.service.image.url if item.service.image else None
        elif (item.company.type.name == "Education"):
            return item.course.image.url if item.course.image else None
        elif (item.company.type.name == "Registration"):
            return item.registration_sub_type.image.url if item.registration_sub_type.image else None
        elif (item.company.type.name == "Product"):
            return item.product.image.url if item.product.image else None
        
        return None

    def item_enclosure_length(self, item):
        if (item.company.type.name == "Service"):
            return item.service.image.size if item.service.image else 0
        elif (item.company.type.name == "Education"):
            return item.course.image.size if item.course.image else 0
        elif (item.company.type.name == "Registration"):
            return item.registration_sub_type.image.size if item.registration_sub_type.image else 0
        elif (item.company.type.name == "Product"):
            return item.product.image.size if item.product.image else 0
        
        return 0

    def item_enclosure_mime_type(self, item):
        if (item.company.type.name == "Service"):
            return "image/jpeg" if item.service.image else None
        elif (item.company.type.name == "Education"):
            return "image/jpeg" if item.course.image else None
        elif (item.company.type.name == "Registration"):
            return "image/jpeg" if item.registration_sub_type.image else None
        elif (item.company.type.name == "Product"):
            return "image/jpeg" if item.product.image else None

        return  None

    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.description  # Raw HTML content (escaped inside CDATA)
        }

# Optional: Serve with XML stylesheet
class StyledCompanyFeed(CompanyFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response


class ContactFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug):
        return get_object_or_404(Company, slug=company_slug)

    def title(self, obj):
        return f"{obj.name} - Contact Information Feed"

    def link(self, obj):
        return f"/{obj.slug}/contact_us/feed/"

    def description(self, obj):
        return f"Latest contact and location updates for {obj.name}"

    def items(self, obj):
        return [ContactUs.objects.filter(company=obj).first()]

    def item_title(self, item):
        return f"Contact update on {item.updated.strftime('%Y-%m-%d')}"

    def item_description(self, item):
        content = f"""
            <p><strong>Address:</strong> {(item.address)}</p>
            <p><strong>Phone:</strong> {(item.phone)}</p>
            <p><strong>Email:</strong> {(item.email)}</p>
        """
        return {
            'content_encoded': content  # Raw HTML content (escaped inside CDATA)
        }

    def item_link(self, item):
        return f"/{item.company.slug}/contact_us/"

    def item_pubdate(self, item):
        return item.updated
    
    def item_extra_kwargs(self, item):
        content = f"""
            <p><strong>Address:</strong> {(item.address)}</p>
            <p><strong>Phone:</strong> {(item.phone)}</p>
            <p><strong>Email:</strong> {(item.email)}</p>
        """
        return {
            'content_encoded': content  # Raw HTML content (escaped inside CDATA)
        }

# Optional: Serve with XML stylesheet
class StyledContactFeed(ContactFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyAboutFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug):
        return get_object_or_404(AboutUs, company__slug=company_slug)

    def title(self, obj):
        return f"About {obj.company.name} - Company Overview"

    def link(self, obj):
        return f"/{obj.company.slug}/about_us/feed/"

    def description(self, obj):
        return Truncator(strip_tags(obj.content or obj.company.meta_description or "")).words(50)

    def items(self, obj):
        return [obj] 

    def item_title(self, item):
        return f"About {item.company.name}"

    def item_description(self, item):
        return Truncator(strip_tags(item.content or item.company.meta_description or "")).words(100)

    def item_link(self, item):
        return f"/{item.company.slug}/about_us/"

    def item_pubdate(self, item):
        return item.updated or item.created
    
    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.content
        }


# Optional: Serve with XML stylesheet
class StyledCompanyAboutFeed(CompanyAboutFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyPrivacyPolicyFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug):
        return get_object_or_404(PrivacyPolicy, company__slug=company_slug)

    def title(self, obj):
        return f"{obj.company.name} - Privacy Policy"

    def link(self, obj):
        return f"/{obj.company.slug}/privacy-policy/feed/"

    def description(self, obj):
        return f"Latest updates to {obj.company.name}'s privacy policy."

    def items(self, obj):
        # Since it's a single page, we return one item
        return [obj]

    def item_title(self, item):
        return f"{item.company.name} Privacy Policy"

    def item_description(self, item):
        return Truncator(strip_tags(item.content or "")).words(100)

    def item_link(self, item):
        return f"/{item.company.slug}/privacy-policy/"

    def item_pubdate(self, item):
        return item.updated if item.updated else item.created
    
    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.content
        }


# Optional: Serve with XML stylesheet
class StyledCompanyPrivacyPolicyFeed(CompanyPrivacyPolicyFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyTermsAndConditionsFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug):
        return get_object_or_404(TermsAndCondition, company__slug=company_slug)

    def title(self, obj):
        return f"{obj.company.name} - Terms & Conditions"

    def link(self, obj):
        return f"/{obj.company.slug}/terms_and_conditions/feed/"

    def description(self, obj):
        return f"Latest updates to {obj.company.name}'s terms and conditions."

    def items(self, obj):
        return [obj]

    def item_title(self, item):
        return f"{item.company.name} Terms & Conditions"

    def item_description(self, item):
        return Truncator(strip_tags(item.content or "")).words(100)

    def item_link(self, item):
        return f"/{item.company.slug}/terms_and_conditions/"

    def item_pubdate(self, item):
        return item.updated_at if item.updated_at else item.created_at
    
    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.content
        }


# Optional: Serve with XML stylesheet
class StyledCompanyTermsAndConditionsFeed(CompanyTermsAndConditionsFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyShippingAndDeliveryPolicyFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug):
        return get_object_or_404(ShippingAndDeliveryPolicy, company__slug=company_slug)

    def title(self, obj):
        return f"{obj.company.name} - Shipping & Delivery Policy"

    def link(self, obj):
        return f"/{obj.company.slug}/shipping_and_delivery_policy/feed/"

    def description(self, obj):
        return f"Latest updates to {obj.company.name}'s terms and conditions."

    def items(self, obj):
        return [obj]

    def item_title(self, item):
        return f"{item.company.name} Shipping & Delivery Policy"

    def item_description(self, item):
        return Truncator(strip_tags(item.content or "")).words(100)

    def item_link(self, item):
        return f"/{item.company.slug}/shipping_and_delivery_policy/"

    def item_pubdate(self, item):
        return item.updated if item.updated else item.created
    
    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.content
        }


# Optional: Serve with XML stylesheet
class StyledCompanyShippingAndDeliveryPolicyFeed(CompanyShippingAndDeliveryPolicyFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyCancellationAndRefundPolicyFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug):
        return get_object_or_404(CancellationAndRefundPolicy, company__slug=company_slug)

    def title(self, obj):
        return f"{obj.company.name} - Cancellation & Refund Policy"

    def link(self, obj):
        return f"/{obj.company.slug}/cancellation_and_refund_policy/feed/"

    def description(self, obj):
        return f"Latest updates to {obj.company.name}'s terms and conditions."

    def items(self, obj):
        return [obj]

    def item_title(self, item):
        return f"{item.company.name} Cancellation & Refund Policy"

    def item_description(self, item):
        return Truncator(strip_tags(item.content or "")).words(100)

    def item_link(self, item):
        return f"/{item.company.slug}/cancellation_and_refund_policy/"

    def item_pubdate(self, item):
        return item.updated if item.updated else item.created
    
    def item_extra_kwargs(self, item):
        return {
            'content_encoded': item.content
        }


# Optional: Serve with XML stylesheet
class StyledCompanyCancellationAndRefundPolicyFeed(CompanyCancellationAndRefundPolicyFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyFaqFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug):
        return get_object_or_404(Company, slug=company_slug)

    def title(self, obj):
        return f"{obj.name} - FAQ Feed"

    def link(self, obj):
        return f"/{obj.slug}/faqs/feed/"

    def description(self, obj):
        return f"Frequently Asked Questions for {obj.name}"

    def items(self, obj):
        return FAQ.objects.filter(company=obj).order_by("-updated")[:20]

    def item_title(self, item):
        return escape(item.question)

    def item_description(self, item):
        return f"<p>{escape(item.answer)}</p>"    

    def item_link(self, item):
        return f"/{item.company.slug}/faqs/"

    def item_pubdate(self, item):
        return item.updated

# Optional: Serve with XML stylesheet
class StyledCompanyFaqFeed(CompanyFaqFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyBlogFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug):
        return get_object_or_404(Company, slug=company_slug)

    def title(self, obj):
        return f"{obj.name} Blog Feed"

    def link(self, obj):
        return f"/{obj.slug}/blog/feed/"

    def description(self, obj):
        return f"Latest blog posts by {obj.name}"

    def items(self, obj):
        return Blog.objects.filter(company=obj).order_by("-updated")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return Truncator(strip_tags(item.content)).words(30)

    def item_link(self, item):
        return f"/{item.company.slug}/blog/{item.slug}/"

    def item_pubdate(self, item):
        return item.updated

    def item_author_name(self, item):
        return item.company.name

    def item_guid(self, item):
        return f"{item.pk}-{item.slug}"

    def item_enclosure_url(self, item):
        return getattr(item.image, 'url', None) if hasattr(item, 'image') else None

    def item_extra_kwargs(self, item):
        return {'enclosure': self.item_enclosure_url(item)}


# Optional: Serve with XML stylesheet
class StyledCompanyBlogFeed(CompanyBlogFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response
    

class CompanyBlogDetailFeed(Feed):
    feed_type = ContentEncodedFeed

    def get_object(self, request, company_slug, blog_slug):
        return get_object_or_404(Blog, company__slug=company_slug, slug=blog_slug)

    def title(self, obj):
        return obj.title

    def link(self, obj):
        return f"/{obj.company.slug}/blog/{obj.slug}/feed/"

    def description(self, obj):
        return obj.meta_description or Truncator(strip_tags(obj.content)).words(30)

    def items(self, obj):
        return [obj]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return Truncator(strip_tags(item.content)).words(50)

    def item_link(self, item):
        return f"/{item.company.slug}/blog/{item.slug}/"

    def item_pubdate(self, item):
        return item.updated or item.created

    def item_author_name(self, item):
        return item.company.name

    def item_guid(self, item):
        return f"{item.pk}-{item.slug}"

    def item_enclosure_url(self, item):
        return getattr(item.image, 'url', None) if hasattr(item, 'image') else None

    def item_extra_kwargs(self, item):
        return {
            'enclosure': self.item_enclosure_url(item),
            'content_encoded': item.content
            }


# Optional: Serve with XML stylesheet
class StyledCompanyDetailBlogFeed(CompanyBlogDetailFeed):
    def __call__(self, request, *args, **kwargs):
        feedgen = self.get_feed(self.get_object(request, *args, **kwargs), request)
        response = HttpResponse(content_type=feedgen.content_type)
        response.write('<?xml version="1.0" encoding="utf-8"?>\n')
        response.write('<?xml-stylesheet type="text/xsl" href="/static/rss-stylesheet.xsl"?>\n')
        feedgen.write(response, 'utf-8')
        return response