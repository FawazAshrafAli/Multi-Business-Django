from rest_framework import serializers
from django.conf import settings

from utility.text import clean_string

from service.models import (
    Service, Category, ServiceDetail, Feature, VerticalBullet,
    VerticalTab, HorizontalBullet, HorizontalTab, Table,
    Timeline, BulletPoints, Faq, Enquiry, MultiPageVerticalBullet,
    MultiPageVerticalTab, MultiPageHorizontalTab, MultiPageHorizontalBullet,
    MultiPageTimeline, MultiPageTable, MultiPageBulletPoint, 
    MultiPageFaq, MultiPageFeature, MultiPage, SubCategory, 
    TextEditor
    )
from locations.models import UniqueState
from company.models import Testimonial

from company_api.serializers import CompanySerializer, TestimonialSerializer
from meta_api.serializers import MetaTagSerializer

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["id", "question", "answer", "slug"]    
    

class TextEditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextEditor
        fields = ["id", "text_editor_title", "content", "slug"]
    

class MiniServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only = True)
    sub_category_name = serializers.CharField(source="sub_category.name", read_only = True)
    duration_count = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["id",
            "name", "image_url", "category_name", 
            "price", "sub_category_name", "duration_count"    
            ]

        read_only_fields = fields

    def get_duration_count(self, obj):
        try:
            return obj.duration.days
        except AttributeError:
            return None

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None


class ServiceListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only = True)
    sub_category_name = serializers.CharField(source="sub_category.name", read_only = True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["id",
            "name", "image_url", "category_name", 
            "price", "slug", "sub_category_name",            
            ]

        read_only_fields = fields
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None
    

class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only = True)
    category_slug = serializers.CharField(source="category.slug", read_only = True)
    sub_category_name = serializers.CharField(source="sub_category.name", read_only = True)
    sub_category_slug = serializers.CharField(source="sub_category.slug", read_only = True)
    duration_count = serializers.CharField(source="duration.days", read_only = True)
    company_social_medias = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only = True)
    company_logo_url = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["id",
            "name", "image_url", "company_name", "category_name", 
            "duration_count", "price", "company_logo_url", 
            "company_social_medias", "slug", "sub_category_name",
            "faqs", "testimonials", "category_slug", 
            "sub_category_slug"
            ]

        read_only_fields = ["id","company_name"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None
    
    def get_company_logo_url(self, obj):
        request = self.context.get('request')
        if obj.company and hasattr(obj.company, 'logo') and hasattr(obj.company.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.company.logo.url)
            return f"{settings.SITE_URL}{obj.company.logo.url}"
        
        return None    
    
    def get_company_social_medias(self, obj):
        if not hasattr(obj, 'company') or not obj.company:
            return []
        
        try:
            return obj.company.social_media_links
        except AttributeError:
            return []
        
    def get_faqs(self, obj):
        if not obj:
            return None
        
        faqs = Faq.objects.filter(service = obj)[:15]

        serializers = FaqSerializer(faqs, many=True)

        return serializers.data
    
    def get_testimonials(self, obj):
        if not obj:
            return None
        
        testimonials = Testimonial.objects.filter(company = obj.company)

        serializer = TestimonialSerializer(testimonials, many=True)

        return serializer.data    


class CategorySerializer(serializers.ModelSerializer):    
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id","name", "slug", "updated", "image_url"]
        
    def get_image_url(self, obj):
        request = self.context.get('request')

        service = obj.services.filter(image__isnull = False).exclude(image = "").order_by("created").first()

        if service and service.image and hasattr(service.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(service.image.url)
            return f"{settings.SITE_URL}{service.image.url}"
        
        return None    
    

class SubCategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    url = serializers.CharField(source="computed_url", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    price = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ["id",
            "name", "slug", "updated", "image_url", "category_name", 
            "category_slug", "url", "company_name", "price",
            "duration", "starting_title", "ending_title", "content",
            "faqs", "location_slug"
            ]

    read_only_fields = "__all__"  

    def get_faqs(self, obj):
        if obj.faqs:
            faqs = list(obj.faqs.values_list("question", "answer"))  
            
            return faqs
        
        return None

    def get_image_url(self, obj):
        request = self.context.get('request')

        service = obj.services.filter(image__isnull = False).exclude(image = "").order_by("created").first()

        if service and service.image and hasattr(service.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(service.image.url)
            return f"{settings.SITE_URL}{service.image.url}"
        
        return None

    def get_price(self, obj):
        if hasattr(obj, "services"):
            service_obj = obj.services.filter(price__isnull = False).first()

            if service_obj and service_obj.price:
                return service_obj.price

        return None
    
    def get_duration(self, obj):
        if hasattr(obj, "services"):
            service_obj = obj.services.filter(duration__isnull = False).first()

            if service_obj and service_obj.duration:
                return service_obj.duration

        return None
    
    

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id","feature", "id"]


class VerticalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerticalBullet
        fields = ["id","id", "bullet"]


class HorizontalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorizontalBullet
        fields = ["id","id", "bullet"]

    
class VerticalTabSerializer(serializers.ModelSerializer):
    bullets = VerticalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = VerticalTab
        fields = ["id",
            "id", "heading", "sub_heading", "summary", "bullets"
            ]
        

class HorizontalTabSerializer(serializers.ModelSerializer):
    bullets = HorizontalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = HorizontalTab
        fields = ["id",
            "id", "heading", "summary", "bullets"
            ]
        
        
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["id",
            "id", "heading"
            ]


class BulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulletPoints
        fields = ["id",
            "id", "bullet_point"
            ]
        

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ["id",
            "id", "heading", "summary"
            ]


class MiniDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    name = category_name = serializers.CharField(source="service.name", read_only = True)
    category_name = serializers.CharField(source="service.category.name", read_only = True)
    sub_category_name = serializers.CharField(source="service.sub_category.name", read_only = True)
    duration_count = serializers.SerializerMethodField()
    price = serializers.CharField(source="service.price", read_only = True)
           
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    company_sub_type = serializers.CharField(source="company.sub_type", read_only=True)
    company_logo_url = serializers.SerializerMethodField()
    url = serializers.CharField(source="computed_url", read_only=True)

    class Meta:
        model = ServiceDetail
        fields = ["id", "name", "image_url", "category_name",
            "meta_description", "service", "company_slug",
            "company_sub_type", "url", "sub_category_name",
            "duration_count", "price", "company_logo_url"
            ] 
    
    def get_duration_count(self, obj):
        try:
            return obj.duration.days
        except AttributeError:
            return None

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.service.image and hasattr(obj.service.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.service.image.url)
            return f"{settings.SITE_URL}{obj.service.image.url}"
        
        return None
    
    def get_company_logo_url(self, obj):
        request = self.context.get('request')
        if obj.company.logo and hasattr(obj.company.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.company.logo.url)
            return f"{settings.SITE_URL}{obj.company.logo.url}"
        
        return None  
        

class DetailListSerializer(serializers.ModelSerializer):
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    url = serializers.CharField(source="computed_url", read_only=True)
    service = ServiceListSerializer()

    class Meta:
        model = ServiceDetail
        fields = ["id", "company_slug",
            "meta_title", "meta_description",
            "summary", "service", "slug",
            "url",
        ]

class DetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="service.name", read_only=True)
    image_url = serializers.SerializerMethodField()
    price = serializers.CharField(source="service.price", read_only=True)
    
    features = FeatureSerializer(many=True)
    vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    timelines = TimelineSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)    

    url = serializers.CharField(source="computed_url", read_only=True)
    category_name = serializers.CharField(source="service.category.name", read_only = True)
    category_slug = serializers.CharField(source="service.category.slug", read_only=True)
    sub_category_name = serializers.CharField(source="service.sub_category.name", read_only=True)
    sub_category_slug = serializers.CharField(source="service.sub_category.slug", read_only=True)

    faqs = serializers.SerializerMethodField()

    class Meta:
        model = ServiceDetail
        fields = ["id", "image_url", "name", "price",
            "meta_title", "meta_description",
            "summary", "description", "features", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "meta_tags", "published", "faqs",
            "modified", "updated", "created", "url", 
            "category_name", "category_slug", 
            "sub_category_name", "sub_category_slug", 
            ] 
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.service.image and hasattr(obj.service.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.service.image.url)
            return f"{settings.SITE_URL}{obj.service.image.url}"
        
        return None
    
    def get_faqs(self, obj):
        if not obj:
            return None
        
        faqs = obj.service.faqs.all()[:15]

        serializers = FaqSerializer(faqs, many=True)

        return serializers.data
        

class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    service = serializers.SlugRelatedField(
        queryset=Service.objects.all(),
        slug_field='slug',
        required=True
    )
    
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
        model = Enquiry
        fields = ["id","company", "name", "phone", "email", "service", "state"]
        extra_kwargs = {
            'company': {'required': False}, 
            'name': {'required': True},
        }
    
    def get_company(self, obj):
        return obj.company.slug

    def __init__(self, *args, **kwargs):
        company_slug = kwargs.pop('company_slug', None)
        super().__init__(*args, **kwargs)
        
        if company_slug:
            self.fields['service'].queryset = Service.objects.filter(
                company__slug=company_slug,                
            )

    def validate(self, data):
        # Clean string fields
        cleaned_data = {}
        string_fields = ['name']
        
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
        
        return data


class MultipageFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFeature
        fields = ["id","feature", "id"]


class MultipageVerticalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageVerticalBullet
        fields = ["id","id", "bullet"]


class MultipageHorizontalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageHorizontalBullet
        fields = ["id","id", "bullet"]

    
class MultipageVerticalTabSerializer(serializers.ModelSerializer):
    bullets = VerticalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = MultiPageVerticalTab
        fields = ["id",
            "id", "heading", "sub_heading", "summary", "bullets"
            ]
        

class MultipageHorizontalTabSerializer(serializers.ModelSerializer):
    bullets = HorizontalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = MultiPageHorizontalTab
        fields = ["id",
            "id", "heading", "summary", "bullets"
            ]
        
        
class MultipageTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTable
        fields = ["id",
            "id", "heading"
            ]


class MultipageBulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageBulletPoint
        fields = ["id",
            "id", "bullet_point"
            ]
        

class MultipageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTimeline
        fields = ["id",
            "id", "heading", "summary"
            ]
        

class MultipageFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFaq
        fields = ["id", "question", "answer", "slug"]


class MultipageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    features = MultipageFeatureSerializer(many=True)
    vertical_tabs = MultipageVerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = MultipageHorizontalTabSerializer(many=True, read_only=True)
    tables = MultipageTableSerializer(many=True, read_only=True)
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    faqs = MultipageFaqSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    text_editors = TextEditorSerializer(many=True, read_only=True)

    company_slug = serializers.CharField(source = "company.slug", read_only=True)
    company_name = serializers.CharField(source = "company.name", read_only=True)

    price = serializers.CharField(source = "service.price", read_only=True)    

    slider_services = MiniDetailSerializer(many=True)

    class Meta:
        model = MultiPage
        fields = ["id", "image_url", "price",
            "title", "summary", "description", "slider_services", "features", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "faqs", "meta_tags", "published",
            "modified", "meta_description", "company_slug", "url_type",
            "rating", "rating_count", "company_name",
            "sub_title", "meta_title", "text_editors"
            ]
        
        read_only = fields        

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.service.image and hasattr(obj.service.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.service.image.url)
            return f"{settings.SITE_URL}{obj.service.image.url}"
        
        return None 
        
