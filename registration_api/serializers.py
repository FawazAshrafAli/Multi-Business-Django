from rest_framework import serializers
from utility.text import clean_string
from django.conf import settings
from django.db.models import Avg

from registration.models import (
    RegistrationSubType, RegistrationDetailPage, Feature, VerticalBullet, 
    HorizontalBullet, VerticalTab, HorizontalTab, Table, BulletPoint, 
    Timeline, RegistrationType, Faq, Enquiry, Registration,

    MultiPageFeature, MultiPageFaq, MultiPage, MultiPageBulletPoint,
    MultiPageHorizontalBullet, MultiPageHorizontalTab, MultiPageTable,
    MultiPageTimeline,
    MultiPageVerticalBullet, MultiPageVerticalTab, TextEditor
    )
from locations.models import UniqueState

from company_api.serializers import CompanySerializer, TestimonialSerializer
from meta_api.serializers import MetaTagSerializer, MiniMetaTagSerializer

class FaqSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    class Meta:
        model = Faq
        fields = ["id", "company", "question", "answer", "slug"]

    def get_company(self, obj):
        if hasattr(obj, "company"):
            return {"name": obj.company.name, "slug": obj.company.slug}
        
        return {}
    
    
class TextEditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextEditor
        fields = ["id", "text_editor_title", "content", "slug"]


class SubTypeSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)
    type_slug = serializers.CharField(source='type.slug', read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)  
    company_name = serializers.CharField(source="company.name", read_only=True)  
    company_contact = serializers.CharField(source="company.phone1", read_only=True)  
    price = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField() 
    image_url = serializers.SerializerMethodField()
    company_logo_url = serializers.SerializerMethodField()
    url = serializers.CharField(source="computed_url", read_only=True)
    duration = serializers.SerializerMethodField()
    full_title = serializers.CharField(source="get_full_title", read_only=True)
    faqs = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationSubType
        fields = ["id",
            "name", "type_name", "company_slug", "description", "slug",
            "price", "type_slug", "company_name", "duration",
            "rating", "updated", "image_url", "url", "location_slug",
            "full_title", "starting_title", "ending_title", "faqs",
            "content", "hide_faqs", "testimonials", "company_contact",
            "company_logo_url"
            ]
        
        read_only_fields = fields    

    def get_rating(self, obj):
        if not hasattr(obj, "company"):
            return 0
        
        testimonials = obj.company.testimonials.values_list("rating", flat=True)

        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0    

    def get_price(self, obj):
        if hasattr(obj, "registrations"):
            registration_obj = obj.registrations.filter(price__isnull = False).first()

            if registration_obj and registration_obj.price:
                return registration_obj.price

        return None
    
    def get_duration(self, obj):
        if hasattr(obj, "registrations"):
            registration_obj = obj.registrations.filter(time_required__isnull = False).first()

            if registration_obj and registration_obj.time_required:
                return registration_obj.time_required

        return None

    def get_testimonials(self, obj):
        if not obj.company: 
            return None
        
        testimonials = obj.company.testimonials

        serializer = TestimonialSerializer(testimonials, many=True)

        return serializer.data
    
    def get_image_url(self, obj):
        if not hasattr(obj, "registrations"):
            return None

        first_registration_with_image = obj.registrations.filter(image__isnull = False).exclude(image = "").order_by("created").first()        

        if first_registration_with_image:
            request = self.context.get('request')
            if first_registration_with_image.image and hasattr(first_registration_with_image.image, 'url'):
                if request is not None:
                    return request.build_absolute_uri(first_registration_with_image.image.url)
                return f"{settings.SITE_URL}{first_registration_with_image.image.url}"
            
    def get_company_logo_url(self, obj):
        if not hasattr(obj, "company"):
            return None
        
        company = obj.company

        request = self.context.get('request')
        if hasattr(company.logo, 'url'):
            if request is not None:
                return request.build_absolute_uri(company.logo.url)
            return f"{settings.SITE_URL}{company.logo.url}"
            
    def get_faqs(self, obj):
        if not hasattr(obj, "faqs"):
            return None
        
        return list(obj.faqs.values("question", "answer"))
        

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id","feature", "id"]


class VerticalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerticalBullet
        fields = ["id", "bullet"]


class HorizontalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorizontalBullet
        fields = ["id", "bullet"]

    
class VerticalTabSerializer(serializers.ModelSerializer):
    bullets = VerticalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = VerticalTab
        fields = ["id",
            "heading", "sub_heading", "summary", "bullets"
            ]
        

class HorizontalTabSerializer(serializers.ModelSerializer):
    bullets = HorizontalBulletSerializer(many=True, read_only=True)

    class Meta:
        model = HorizontalTab
        fields = ["id",
            "heading", "summary", "bullets"
            ]
        
        
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["id",
            "heading"
            ]


class BulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulletPoint
        fields = ["id",
            "bullet_point"
            ]
        

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ["id",
            "heading", "summary"
            ]


class MiniRegistrationSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    type_name = serializers.CharField(source="registration_type.name", read_only = True)

    class Meta:
        model = Registration
        fields = ["id",
            "title", "image_url", "sub_type", "price", "type_name"
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None


class RegistrationListSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source="registration_type.name", read_only=True)
    sub_type_name = serializers.CharField(source="sub_type.name", read_only=True)
    price = serializers.CharField(source="sub_type.price", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = ["id",
            "title", "image_url", "type_name", "sub_type_name", "price",
            "slug",
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        
        return None


class RegistrationSerializer(serializers.ModelSerializer):
    sub_type  = SubTypeSerializer()
    image_url = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField() 

    class Meta:
        model = Registration
        fields = ["id",
            "title", "image_url", "sub_type", "price",
            "time_required", "required_documents", "additional_info",
            "slug", "updated", "rating"
        ]

    def get_rating(self, obj):
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


class MiniDetailSerializer(serializers.ModelSerializer):
    registration = MiniRegistrationSerializer()
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    company_sub_type = serializers.CharField(source="company.sub_type", read_only=True)
    url = serializers.CharField(source="computed_url", read_only=True)
    company_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationDetailPage
        fields = ["id",
            "registration", "meta_description", "company_slug",
            "company_sub_type", "url", "company_logo_url"
            ]      

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

    title = serializers.CharField(source="registration.title", read_only=True)
    type_name = serializers.CharField(source="registration.registration_type.name", read_only=True)
    sub_type_name = serializers.CharField(source="registration.sub_type.name", read_only=True)
    price = serializers.CharField(source="registration.price", read_only=True)
    time_required = serializers.CharField(source="registration.time_required", read_only=True)
    image_url = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = RegistrationDetailPage
        fields = ["id", "title", "company_slug", "image_url",
            "meta_title", "meta_description",
            "summary", "slug", "url", "type_name",
            "sub_type_name", "price", "time_required",
            "company_name"
            ]
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.registration.image and hasattr(obj.registration.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.registration.image.url)
            return f"{settings.SITE_URL}{obj.registration.image.url}"
        
        return None


class DetailSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="registration.title", read_only=True)    
    image_url = serializers.SerializerMethodField()
    
    features = FeatureSerializer(many=True)
    vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    timelines = TimelineSerializer(many=True, read_only=True)
    faqs = serializers.SerializerMethodField()
    meta_tags = serializers.SerializerMethodField()
    url = serializers.CharField(source="computed_url", read_only=True)

    sub_type_name = serializers.CharField(source="registration.sub_type.name", read_only=True)
    sub_type_slug = serializers.CharField(source="registration.sub_type.slug", read_only=True)

    type_name = serializers.CharField(source="registration.registration_type.name", read_only=True)
    type_slug = serializers.CharField(source="registration.registration_type.slug", read_only=True)

    price = serializers.CharField(source="registration.price", read_only=True)

    company_rating = serializers.CharField(source="get_company_rating", read_only=True)

    class Meta:
        model = RegistrationDetailPage
        fields = ["id", "title", "image_url",
            "meta_title", "meta_description",
            "summary", "description", "features", "slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "faqs", "meta_tags", "published",
            "modified", "created", "updated",
            "url", "company_rating", "price",
            "type_name", "type_slug", "sub_type_name", "sub_type_slug"
            ]
    
    def get_faqs(self, obj):
        if obj.registration:
            faqs = obj.registration.faqs.values("question", "answer", "slug")[:15]

            if faqs:
                serializer = FaqSerializer(faqs, many=True)
                return serializer.data
            
        return []

    def get_meta_tags(self, obj):
        meta_tags = obj.meta_tags.values("name", "slug", "meta_description")[:12]

        if meta_tags:
            serializer = MetaTagSerializer(meta_tags, many=True)
            return serializer.data
            
        return []
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.registration.image and hasattr(obj.registration.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.registration.image.url)
            return f"{settings.SITE_URL}{obj.registration.image.url}"
        
        return None
            


class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    registration = serializers.SlugRelatedField(
        queryset=Registration.objects.all(),
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
        fields = ["id","company", "name", "phone", "email", "registration", "state"]
        extra_kwargs = {
            'company': {'required': False},  # Typically set server-side
            'name': {'required': True}
        }
    
    def get_company(self, obj):
        return obj.company.slug

    def __init__(self, *args, **kwargs):
        company_slug = kwargs.pop('company_slug', None)
        super().__init__(*args, **kwargs)
        
        if company_slug:
            self.fields['registration'].queryset = Registration.objects.filter(
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

class MultipageFaqSerializer(serializers.ModelSerializer):

    class Meta:
        model = MultiPageFaq
        fields = ["id", "question", "answer", "slug"]

class MultipageFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFeature
        fields = ["id","feature", "id"]


class MultipageVerticalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageVerticalBullet
        fields = ["id", "bullet"]


class MultipageHorizontalBulletSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageHorizontalBullet
        fields = ["id", "bullet"]

    
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


class MultipageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    features = MultipageFeatureSerializer(many=True, read_only=True)
    vertical_tabs = MultipageVerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = MultipageHorizontalTabSerializer(many=True, read_only=True)
    tables = MultipageTableSerializer(many=True, read_only=True)
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    faqs = MultipageFaqSerializer(many=True, read_only=True)
    meta_tags = serializers.SerializerMethodField()
    text_editors = TextEditorSerializer(many=True, read_only=True)
    time_required = serializers.CharField(source="registration.time_required", read_only=True)

    sub_type_name = serializers.CharField(source="registration.sub_type.name", read_only=True)
    sub_type_slug = serializers.CharField(source="registration.sub_type.slug", read_only=True)

    type_name = serializers.CharField(source="registration.registration_type.name", read_only=True)
    type_slug = serializers.CharField(source="registration.registration_type.slug", read_only=True)

    price = serializers.CharField(source="registration.price", read_only=True)

    slider_registrations = MiniDetailSerializer(many = True)

    company_name = serializers.CharField(source="company.name", read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)

    class Meta:
        model = MultiPage
        fields = ["id", "image_url", "company_name", "company_slug",
            "title", "slug", "summary", "description", "slider_registrations",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points", "features", "slug",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "faqs", "meta_tags", "published",
            "modified", "meta_description", "url_type",
            "rating", "rating_count", "time_required",
            "type_name", "type_slug", "price",
            "sub_type_name", "sub_type_slug", "sub_title", "meta_title", "text_editors"
            ]
        
        read_only = fields
    
    def get_meta_tags(self, obj):
        if not obj.meta_tags:
            return None
        
        meta_tags = obj.meta_tags.all()[0:12]

        serializer = MiniMetaTagSerializer(meta_tags, many=True)

        return serializer.data
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.registration.image and hasattr(obj.registration.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.registration.image.url)
            return f"{settings.SITE_URL}{obj.registration.image.url}"
        
        return None


class TypeSerializer(serializers.ModelSerializer):    

    class Meta:
        model = RegistrationType
        fields = ["id",
            "name", "company", "description", "slug",
            "updated"
            ]
        
        read_only_fields = fields            
        