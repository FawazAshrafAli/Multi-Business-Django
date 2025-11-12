from rest_framework import serializers
from django.conf import settings

from company.models import Company, CompanyType, Client, ContactEnquiry, Testimonial, Banner

from blog_api.serializers import BlogSerializer
from meta_api.serializers import MetaTagSerializer
from custom_pages_api.serializers import FaqSerializer
from locations.models import UniqueState

from utility.text import clean_string

class ClientSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ["id","name", "image_url", "url", "slug"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None
    

class TestimonialSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    place_name = serializers.CharField(source = "place.name", read_only = True)
    company_rating = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = ["id",
            "name", "image_url", "slug", "client_company", "place_name",
            "text", "rating", "company_rating", "created"
            ]
        
    
    def get_company_rating(self, obj):
        from django.db.models import Avg

        if not obj.company:
            return 0
        
        testimonials = obj.company.testimonials.values_list("rating", flat=True)

        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0
        
    

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None
    


class MiniCompanySerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    type_slug = serializers.CharField(source = "type.slug", read_only=True)    
    company_type = serializers.CharField(source = "type.name", read_only=True)    
    testimonials = serializers.SerializerMethodField()
    sub_categories = serializers.SerializerMethodField()
    price_range = serializers.CharField(source = "get_price_range", read_only=True)

    class Meta:
        model = Company 
        fields = ["id",
            "name", "logo_url", "description", 
            "slug", "summary", "get_absolute_url",  
            "company_type", "meta_title",
            "meta_description", "type_slug",
            "slug", "testimonials", "sub_categories",
            "price_range"
        ]

    def get_sub_categories(self, obj):        

        if not obj.type:
            return None
        
        if obj.type.name == "Education":
            specializations = obj.specializations.order_by("name")[:8]

            return [{
                "title": specialization.name,
                "slug": specialization.slug,
                "url": f'/{specialization.company.slug}/{specialization.program.slug}/{specialization.slug}'
            } for specialization in specializations]
        
        elif obj.type.name == "Service":
            sub_categories = obj.service_sub_categories.order_by("name")[:8]

            return [{
                "title": sub_category.name,
                "slug": sub_category.slug,
                "url": f'/{sub_category.company.slug}/{sub_category.category.slug}/{sub_category.slug}'
            } for sub_category in sub_categories]
        
        elif obj.type.name == "Product":
            sub_categories = obj.product_sub_categories.order_by("name")[:8]

            return [{
                "title": sub_category.name,
                "slug": sub_category.slug,
                "url": f'/{sub_category.company.slug}/{sub_category.category.slug}/{sub_category.slug}'
            } for sub_category in sub_categories]
        
        elif obj.type.name == "Registration":
            sub_types = obj.sub_types.order_by("name")[:8]

            return [{
                "title": sub_type.name,
                "slug": sub_type.slug,
                "url": f'/{sub_type.company.slug}/{sub_type.type.slug}/{sub_type.slug}'
            } for sub_type in sub_types]
        
        else: return None

    def get_testimonials(self, obj):
        if obj.testimonials:
            testimonials = obj.testimonials.order_by("order")[:12]
            serializer = TestimonialSerializer(testimonials, many=True)
            return serializer.data
        
        return []

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.logo.url)
            return f"{settings.SITE_URL}{obj.logo.url}"
        return None
    

class NormalFooterCompanySerializer(serializers.ModelSerializer):
    multipages = serializers.SerializerMethodField()

    class Meta:
        model = Company 
        fields = ["id", "name", "slug", "multipages"]

    
    def get_multipages(self, obj):
        if not obj.type:
            return None

        multipage_sources = [
            obj.course_multipages.filter(home_footer_visibility = True, course_region = "all"),
            obj.service_multipages.filter(home_footer_visibility = True, service_region = "all"),
            obj.product_multipages.filter(home_footer_visibility = True, product_region = "all"),
            obj.registration_multipages.filter(home_footer_visibility = True, registration_region = "all"),
        ]

        for qs in multipage_sources:
            if qs.exists():
                return list(
                    qs.order_by("?").values("title", "slug", "url_type")
                )
        
        return []
    

class LocationBasedFooterCompanySerializer(serializers.ModelSerializer):
    multipages = serializers.SerializerMethodField()

    class Meta:
        model = Company 
        fields = ["id", "name", "slug", "multipages"]

    
    def get_multipages(self, obj):
        if not obj.type:
            return None

        multipage_sources = [
            obj.course_multipages,
            obj.service_multipages,
            obj.product_multipages,
            obj.registration_multipages,
        ]

        for qs in multipage_sources:
            if qs.exists():
                return list(
                    qs.order_by("?").values("title", "slug", "url_type")[:12]
                )
        
        return []
    

class NavbarCompanySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()
    items_url = serializers.SerializerMethodField()
    company_type = serializers.CharField(source="type.name")

    class Meta:
        model = Company 
        fields = ["id", "name", "slug", "sub_categories", "items_url", "company_type"]

    def get_sub_categories(self, obj):        

        if not obj.type:
            return None
        
        if obj.type.name == "Education":
            specializations = obj.specializations.order_by("name")[:32]

            return [{
                "title": specialization.name,
                "slug": specialization.slug,
                "url": f'/{specialization.company.slug}/{specialization.program.slug}/{specialization.slug}'
            } for specialization in specializations]
        
        elif obj.type.name == "Service":
            sub_categories = obj.service_sub_categories.order_by("name")[:32]

            return [{
                "title": sub_category.name,
                "slug": sub_category.slug,
                "url": f'/{sub_category.company.slug}/{sub_category.category.slug}/{sub_category.slug}'
            } for sub_category in sub_categories]
        
        elif obj.type.name == "Product":
            sub_categories = obj.product_sub_categories.order_by("name")[:32]

            return [{
                "title": sub_category.name,
                "slug": sub_category.slug,
                "url": f'/{sub_category.company.slug}/{sub_category.category.slug}/{sub_category.slug}'
            } for sub_category in sub_categories]
        
        elif obj.type.name == "Registration":
            sub_types = obj.sub_types.order_by("name")[:32]

            return [{
                "title": sub_type.name,
                "slug": sub_type.slug,
                "url": f'/{sub_type.company.slug}/{sub_type.type.slug}/{sub_type.slug}'
            } for sub_type in sub_types]
        
        else: return None

    def get_items_url(self, obj):        
        if not obj.type:
            return None
        
        if obj.type.name == "Education":
            return "courses"            
        
        elif obj.type.name == "Service":
            return "more-services"
        
        elif obj.type.name == "Product":
            return "products"
        
        elif obj.type.name == "Registration":
            return "filings"
        
        else: return None


class BaseCompanySerializer(serializers.ModelSerializer):
    blogs_count = serializers.SerializerMethodField()
    price_range = serializers.CharField(source = "get_price_range", read_only=True)

    class Meta:
        model = Company 
        fields = ["id", "name", "slug", "sub_type", "blogs_count", "price_range"]

    def get_blogs_count(self, obj):
        if obj.blogs:
            return obj.blogs.count()
        
        return 0

class InnerPageCompanySerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    blogs = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    meta_tags = serializers.SerializerMethodField()
    company_type = serializers.CharField(source = "type.name", read_only=True)    
    testimonials = serializers.SerializerMethodField()
    clients = serializers.SerializerMethodField()
    client_slider_heading = serializers.CharField(source="get_client_slider_heading")
    place_name = serializers.CharField(source="get_place_name")
    district_name = serializers.CharField(source="get_district_name")
    state_name = serializers.CharField(source="get_state_name")
    pincode = serializers.CharField(source="get_pincode")

    class Meta:
        model = Company 
        fields = ["id",
            "name", "logo_url", "description", 
            "slug", "meta_title",
            "phone1", "phone2", "blogs", "faqs", "whatsapp", 
            "email",  "meta_tags", "meta_description", 
            "favicon_url", "rating", "sub_type", "company_type",
            "testimonials", "clients", "client_slider_heading",
            "place_name", "district_name", "state_name", "pincode"
        ]

    read_only_fields = "__all__"

    def get_clients(self, obj):
        clients = obj.clients.all().order_by("-updated")[0:12]
        serializers = ClientSerializer(clients, many = True)
        return serializers.data

    def get_testimonials(self, obj):
        testimonials = obj.testimonials.all().order_by("-updated")[0:12]
        serializers = TestimonialSerializer(testimonials, many = True)
        return serializers.data

    def get_blogs(self, obj):
        blogs = obj.blogs.filter(
            is_published = True).prefetch_related(
            "meta_tags"
        )[0:12]
        serializers = BlogSerializer(blogs, many = True)
        return serializers.data
    
    def get_faqs(self, obj):
        faqs = obj.faqs.all()[:15]
        serializers = FaqSerializer(faqs, many = True)
        return serializers.data
    
    def get_meta_tags(self, obj):
        meta_tags = obj.meta_tags.all()[0:12]
        serializers = MetaTagSerializer(meta_tags, many = True)
        return serializers.data

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.logo.url)
            return f"{settings.SITE_URL}{obj.logo.url}"
        return None
    
    def get_favicon_url(self, obj):
        request = self.context.get('request')
        if obj.favicon and hasattr(obj.favicon, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.favicon.url)
            return f"{settings.SITE_URL}{obj.favicon.url}"
        return None


class MinimalCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company 
        fields = [
            "id", "name", "sub_type", "slug"
        ]


class FaqCompanySerializer(serializers.ModelSerializer):
    faqs = FaqSerializer(many=True, read_only=True)

    class Meta:
        model = Company 
        fields = [
            "id", "name", "sub_type", "slug", "faqs"
        ]    


class CompanySerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    company_type = serializers.CharField(source = "type.name", read_only=True)    
    blogs = serializers.SerializerMethodField()
    faqs = FaqSerializer(many=True, read_only = True)
    meta_tags = MetaTagSerializer(many=True, read_only = True)
    clients = ClientSerializer(many=True, read_only=True)
    type_slug = serializers.CharField(source = "type.slug", read_only=True)    
    detail_pages = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    items_url = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    rating = serializers.CharField(source = "get_rating", read_only=True) 
    price_range = serializers.CharField(source = "get_price_range", read_only=True)
    testimonials = serializers.SerializerMethodField()
    client_slider_heading = serializers.CharField(source="get_client_slider_heading")

    class Meta:
        model = Company 
        fields = ["id",
            "name", "logo_url", "description" , "categories", 
            "get_absolute_url", "slug", "summary",  
            "company_type", "footer_content", "meta_title",
            "phone1", "phone2", "blogs", "faqs", "whatsapp", 
            "email", "meta_tags", "meta_description", 
            "favicon_url", "price_range", "phone",
            "created", "updated", "clients", "rating",
            "sub_type", "type_slug", "detail_pages",             
            "items_url", "testimonials", "client_slider_heading"
        ]

    read_only_fields = "__all__"

    def get_testimonials(self, obj):
        testimonials = obj.testimonials.all()[:12]

        serializer = TestimonialSerializer(testimonials, many=True)
        return serializer.data

    def get_phone(self, obj):
        first_contact_obj_of_company = obj.contacts.first()

        if first_contact_obj_of_company:
            return first_contact_obj_of_company.mobile or first_contact_obj_of_company.tel or None
        
        return None

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.logo.url)
            return f"{settings.SITE_URL}{obj.logo.url}"
        return None
    
    def get_favicon_url(self, obj):
        request = self.context.get('request')
        if obj.favicon and hasattr(obj.favicon, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.favicon.url)
            return f"{settings.SITE_URL}{obj.favicon.url}"
        return None
    
    def get_categories(self, obj):
        return obj.get_categories
    
    def get_blogs(self, obj):
        blogs = obj.get_blogs
        serializer = BlogSerializer(blogs, many=True)

        return serializer.data
    
    def get_detail_pages(self, obj):
        from educational.models import CourseDetail
        from service.models import ServiceDetail
        from product.models import ProductDetailPage
        from registration.models import RegistrationDetailPage

        if not obj.type:
            return None
        
        if obj.type.name == "Education":
            detail_pages = CourseDetail.objects.filter(company = obj).order_by("course__name")

            return [{
                "title": page.course.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.course.program.slug}/{page.course.specialization.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Service":
            detail_pages = ServiceDetail.objects.filter(company = obj).order_by("service__name")

            return [{
                "title": page.service.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.service.category.slug}/{page.service.sub_category.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Product":
            detail_pages = ProductDetailPage.objects.filter(company = obj).order_by("product__name")

            return [{
                "title": page.product.name,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.product.category.slug}/{page.product.sub_category.slug}/{page.slug}'
            } for page in detail_pages]
        
        elif obj.type.name == "Registration":
            detail_pages = RegistrationDetailPage.objects.filter(company = obj).order_by("registration__title")

            return [{
                "title": page.registration.title,
                "slug": page.slug,
                "url": f'/{page.company.slug}/{page.registration.registration_type.slug}/{page.registration.sub_type.slug}/{page.slug}'
            } for page in detail_pages]
        
        else: return None        

    def get_items_url(self, obj):        
        if not obj.type:
            return None
        
        if obj.type.name == "Education":
            return "courses"            
        
        elif obj.type.name == "Service":
            return "services"
        
        elif obj.type.name == "Product":
            return "products"
        
        elif obj.type.name == "Registration":
            return "registrations"
        
        else: return None
    

class CompanyTypeSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)    

    class Meta:
        model = CompanyType
        fields = ["id","name", "slug", "companies", "categories"]


class LocationBasedFooterCompanyTypeSerializer(serializers.ModelSerializer):
    companies = LocationBasedFooterCompanySerializer(many=True, read_only=True)    

    class Meta:
        model = CompanyType
        fields = ["id","name", "slug", "companies"]


class NormalFooterCompanyTypeSerializer(serializers.ModelSerializer):
    companies = NormalFooterCompanySerializer(many=True, read_only=True)    

    class Meta:
        model = CompanyType
        fields = ["id","name", "slug", "companies"]


class NavbarCompanyTypeSerializer(serializers.ModelSerializer):
    companies = NavbarCompanySerializer(many=True, read_only=True)    

    class Meta:
        model = CompanyType
        fields = ["id","name", "slug", "companies"]

    
class MiniCompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = ["id","name"]


class ContactEnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    
    state = serializers.SlugRelatedField(
        queryset=UniqueState.objects.all(),
        slug_field='slug',
        required=True
    )
    
    phone = serializers.RegexField(
        regex=r'^[^A-Za-z]*$',
        error_messages={
            'invalid': 'Phone number must not contain alphabetic characters.'
        },
        required=True
    )
    
    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    
    class Meta:
        model = ContactEnquiry
        fields = ["id","company", "name", "phone", "email", "state", "message"]
        extra_kwargs = {
            'company': {'required': False},
            'name': {'required': True},
            'message': {'required': True}
        }
    
    def get_company(self, obj):
        return obj.company.slug

    def validate(self, data):
        # Clean string fields
        cleaned_data = {}
        string_fields = ['name', 'message']
        
        for field in string_fields:
            value = data.get(field, '').strip()
            if not value:
                raise serializers.ValidationError(
                    {field: f"{field.capitalize()} is required and cannot be empty"}
                )
            cleaned_data[field] = clean_string(value)
        
        # Email validation
        email = data.get('email', '').strip().lower()
        if not email:
            raise serializers.ValidationError({"email": "Email is required"})
        cleaned_data['email'] = email
        
        # Phone validation (already handled by RegexField)
        cleaned_data['phone'] = data['phone']
        
        # Update data with cleaned values
        data.update(cleaned_data)
        
        # Additional business logic validation
        if not self.context.get('request').user.is_authenticated:
            # Example: Spam prevention for anonymous submissions
            if len(data['message']) > 1000:
                raise serializers.ValidationError(
                    {"message": "Message too long (max 1000 characters)"}
                )
        
        return data
    

class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ["id","title", "description", "link", "image_url", "slug"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None