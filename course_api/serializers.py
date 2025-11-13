from rest_framework import serializers
from django.conf import settings

from utility.text import clean_string

from educational.models import  (
    Course, Testimonial, Faq, Enquiry, Program, CourseDetail,
    Feature, VerticalTab, HorizontalTab, Table, BulletPoints, 
    Timeline, VerticalBullet, HorizontalBullet,

    MultiPage, MultiPageFaq, MultiPageFeature, MultiPageBulletPoints,
    MultiPageHorizontalBullet, MultiPageHorizontalTab,
    MultiPageTable, MultiPageTimeline, MultiPageVerticalTab,
    MultiPageVerticalBullet, TextEditor,

    Specialization
    )
from locations.models import UniqueState
from meta_api.serializers import MetaTagSerializer, MiniMetaTagSerializer

class MiniCourseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    program_name = serializers.CharField(source='program.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)     

    class Meta:
        model = Course
        fields = ["id",
            "name", "program_name", "image_url",
            "company_name", "mode", 
            "starting_date", "ending_date", "duration",
            "price", "rating", "rating_count"          
            ]
        
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return None


class TextEditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextEditor
        fields = ["id", "text_editor_title", "content", "slug"]
    

class CourseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    program_name = serializers.CharField(source='program.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_sub_type = serializers.CharField(source='company.sub_type', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)
    program_slug = serializers.CharField(source='program.slug', read_only=True)
    specialization_slug = serializers.CharField(source='specialization.slug', read_only=True)
    specialization_name = serializers.CharField(source='specialization.name', read_only=True)

    class Meta:
        model = Course
        fields = ["id",
            "name", "program_name", "image_url", "company_sub_type",
            "description", "company_name", "company_slug", "mode", 
            "starting_date", "ending_date", "duration", "program_slug",
            "price", "rating", "rating_count", "slug", "specialization_slug",
            "specialization_name"
            ]
        
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
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


class StudentTestimonialSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    course_name = serializers.CharField(source = "course.name", read_only=True)
    course_meta_description = serializers.CharField(source = "course.meta_description", read_only=True)
    place_name = serializers.CharField(source = "place.name", read_only=True)

    class Meta:
        model = Testimonial
        fields = ["id","name", "image_url", "course_name", "place_name", "text", "rating", "slug", "course_meta_description"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}{obj.image.url}"
        return


class CourseFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["id","question", "answer", "slug"]

    
class MiniCourseDetailSerializer(serializers.ModelSerializer):    
    course = MiniCourseSerializer()        
    url = serializers.CharField(read_only=True, source = "computed_url")
    company_sub_type = serializers.CharField(read_only=True, source = "company.sub_type.name")

    class Meta:
        model = CourseDetail
        fields = ["id",
            "meta_description","course","url", "company_sub_type"
            ]
    

class DetailListSerializer(serializers.ModelSerializer):
    company_slug = serializers.CharField(source="company.slug", read_only = True)
    course = CourseSerializer()
    url = serializers.CharField(read_only=True, source = "computed_url")

    class Meta:
        model = CourseDetail
        fields = ["id",
            "meta_title", "meta_description", "company_slug",
            "summary", "course", "slug",
            "published", "url",             
            ]    
        

class DetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    name = serializers.CharField(source="course.name", read_only = True)

    features = FeatureSerializer(many=True)
    vertical_tabs = VerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = HorizontalTabSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    timelines = TimelineSerializer(many=True, read_only=True)
    faqs = CourseFaqSerializer(many=True, read_only=True)
    testimonials = StudentTestimonialSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    item_name = serializers.CharField(source="course.name", read_only = True)
    company_slug = serializers.CharField(source="company.slug", read_only = True)
    url = serializers.CharField(source="computed_url", read_only = True)

    program_name = serializers.CharField(source="course.program.name", read_only=True)
    program_slug = serializers.CharField(source="course.program.slug", read_only=True)
    specialization_name = serializers.CharField(source="course.specialization.name", read_only=True)
    specialization_slug = serializers.CharField(source="course.specialization.slug", read_only=True)

    rating = serializers.CharField(source="get_rating", read_only = True)
    rating_count = serializers.CharField(source="course.rating_count", read_only = True)
    mode = serializers.CharField(source="course.mode", read_only = True)
    starting_date = serializers.CharField(source="course.starting_date", read_only = True)
    ending_date = serializers.CharField(source="course.ending_date", read_only = True)
    duration = serializers.CharField(source="course.duration", read_only = True)
    price = serializers.CharField(source="course.price", read_only = True)

    class Meta:
        model = CourseDetail
        fields = ["id", "image_url", "name",
            "meta_title", "meta_description", "company_slug",
            "summary", "description", "features","slug",
            "vertical_title", "horizontal_title", "vertical_tabs", 
            "horizontal_tabs", "table_title", "tables", "get_data",
            "bullet_title", "bullet_points",
            "timeline_title", "timelines", "toc", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "faqs", "testimonials", "meta_tags", "published",
            "modified", "item_name", "created", "updated", "url", 
            "program_name", "program_slug", "specialization_name", 
            "specialization_slug", "rating", "rating_count", "mode", "starting_date",
            "ending_date", "duration", "price"
            ]    

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.course.image and hasattr(obj.course.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.course.image.url)
            return f"{settings.SITE_URL}{obj.course.image.url}"
        return None


class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    course = serializers.SlugRelatedField(
        queryset=Course.objects.all(),
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
        fields = ["id","company", "name", "phone", "email", "course", "state"]
        extra_kwargs = {
            'company': {'required': False},  # Typically set server-side
            'name': {'required': True},
        }
    
    def get_company(self, obj):
        return obj.company.slug

    def __init__(self, *args, **kwargs):
        company_slug = kwargs.pop('company_slug', None)
        super().__init__(*args, **kwargs)
        
        if company_slug:
            self.fields['course'].queryset = Course.objects.filter(
                company__slug=company_slug,
                is_active=True  # Example of additional filtering
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
    

class ProgramSerializer(serializers.ModelSerializer):    
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ["id","name", "slug", "updated", "image_url"] 

    def get_image_url(self, obj):
        request = self.context.get('request')

        course = obj.courses.filter(image__isnull = False).exclude(image = "").order_by("created").first()

        if course and course.image and hasattr(course.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(course.image.url)
            return f"{settings.SITE_URL}{course.image.url}"
        return None   
    

class SpecializationSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source="program.name", read_only=True)
    program_slug = serializers.CharField(source="program.slug", read_only=True)
    image_url = serializers.SerializerMethodField()
    url = serializers.CharField(source="computed_url", read_only=True)
    price = serializers.SerializerMethodField()
    mode = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Specialization
        fields = [
            "id","name", "slug", "program", 
            "updated", "image_url", "updated",
            "program_name", "program_slug",
            "url", "price", "company_name",
            "mode", "duration"
            ]

    read_only_fields = "__all__"

    def get_price(self, obj):
        if hasattr(obj, "courses"):
            course_obj = obj.courses.filter(price__isnull = False).first()

            if course_obj and course_obj.price:
                return course_obj.price

        return None
    
    def get_mode(self, obj):
        if hasattr(obj, "courses"):
            course_obj = obj.courses.filter(mode__isnull = False).first()

            if course_obj and course_obj.mode:
                return course_obj.mode

        return None
    
    def get_duration(self, obj):
        if hasattr(obj, "courses"):
            course_obj = obj.courses.filter(duration__isnull = False).first()

            if course_obj and course_obj.duration:
                return course_obj.duration

        return None

    def get_image_url(self, obj):
        request = self.context.get('request')

        course = Course.objects.filter(specialization = obj, image__isnull = False).exclude(image = "").order_by("created").first()

        if course and course.image and hasattr(course.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(course.image.url)
            return f"{settings.SITE_URL}{course.image.url}"
        return None
    

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
        model = MultiPageBulletPoints
        fields = ["id",
            "id", "bullet_point"
            ]
        

class MultiPageFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFaq
        fields = ["id",
            "question", "answer", "slug"
        ]
        

class MultipageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageTimeline
        fields = ["id",
            "id", "heading", "summary"
            ]


class MultiPageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    starting_date = serializers.CharField(source="course.starting_date", read_only=True)
    ending_date = serializers.CharField(source="course.ending_date", read_only=True)
    faqs = MultiPageFaqSerializer(many=True, read_only=True)
    meta_tags = serializers.SerializerMethodField()
    mode = serializers.CharField(source="course.mode", read_only=True)
    duration = serializers.CharField(source="course.duration", read_only = True)
    price = serializers.CharField(source="course.price", read_only = True)
    program_name = serializers.CharField(source="course.program.name", read_only=True)
    rating = serializers.CharField(source="get_rating", read_only = True)
    rating_count = serializers.CharField(source="course.rating_count", read_only = True)

    slider_courses = MiniCourseDetailSerializer(many=True)
    features = MultipageFeatureSerializer(many=True)
    vertical_tabs = MultipageVerticalTabSerializer(many=True, read_only=True)
    horizontal_tabs = MultipageHorizontalTabSerializer(many=True, read_only=True)
    tables = MultipageTableSerializer(many=True, read_only=True)
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    text_editors = TextEditorSerializer(many=True, read_only=True)

    class Meta:
        model = MultiPage
        fields = ["id", "image_url",
            "title", "summary", "description", "slug",
            "toc", "mode", "starting_date", "ending_date",
            "faqs", "url_type", "meta_tags", "price",
            "meta_description", "duration", "program_name",
            "meta_title", "rating", "rating_count",

            "slider_courses", "features", "vertical_title", "horizontal_title", 
            "vertical_tabs", "horizontal_tabs", "table_title", "tables", 
            "get_data", "bullet_title", "bullet_points", "text_editors",
            "timeline_title", "timelines", "hide_features", 
            "hide_vertical_tab", "hide_horizontal_tab", "hide_table",
            "hide_bullets", "hide_timeline", "hide_support_languages",
            "published", "modified", "sub_title", "updated", 
            "created"
            ]
        
    read_only_fields = "__all___"
        
    def get_meta_tags(self, obj):
        if not obj.meta_tags:
            return None
        
        meta_tags = obj.meta_tags.all()

        serializer = MiniMetaTagSerializer(meta_tags, many=True)

        return serializer.data
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.course.image and hasattr(obj.course.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.course.image.url)
            return f"{settings.SITE_URL}{obj.course.image.url}"
        return None