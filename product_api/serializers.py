from rest_framework import serializers
from django.conf import settings

from utility.text import clean_string
from datetime import datetime

from product.models import (
    Product, Review, Category, ProductDetailPage, Enquiry, 
    SubCategory, Feature, Timeline,MultiPage,
    Faq, BulletPoint, MultiPageFaq, MultiPageBulletPoint,
    MultiPageFeature, MultiPageTimeline, TextEditor
    )
from locations.models import UniqueState
from meta_api.serializers import MetaTagSerializer, MiniMetaTagSerializer
from django.db.models import Avg

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ["id","question", "answer", "slug"]


class TextEditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextEditor
        fields = ["id", "text_editor_title", "content", "slug"]


class ReviewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    created_date = serializers.CharField(source="computed_created_date", read_only=True)
    image_url = serializers.SerializerMethodField()
    avg_rating = serializers.CharField(source="get_avg_rating", read_only=True)

    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field='slug',
        required=True
    )

    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    
    class Meta:
        model = Review
        fields = ["id",'name', 'text', 'rating', 'created', "product_name", "review_by", "created_date", "product", "email", "image_url", "avg_rating"]
        extra_kwargs = {
            'company': {'required': False},
            'review_by': {'required': True},
            'text': {'required': True},
            'email': {'required': True},
            'rating': {'required': True}
        }

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.product.image and hasattr(obj.product.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.product.image.url)
            return f"{settings.SITE_URL}/{obj.product.image.url}"
        
        return None
    
    def __init__(self, *args, **kwargs):
        company_slug = kwargs.pop('company_slug', None)
        super().__init__(*args, **kwargs)
        
        if company_slug:
            self.fields['product'].queryset = Product.objects.filter(
                company__slug=company_slug,                
            )

    def validate(self, data):
        # Clean string fields
        cleaned_data = {}
        string_fields = ["id",'review_by', 'text']
        
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

        rating = data.get('rating', '')
        cleaned_data['rating'] = rating if rating else 0

        
        # Update data with cleaned values
        data.update(cleaned_data)
        
        # Additional business logic validation
        if not self.context.get('request').user.is_authenticated:
            # Example: Spam prevention for anonymous submissions
            if len(data['text']) > 1000:
                raise serializers.ValidationError(
                    {"message": "Message too long (max 1000 characters)"}
                )
        
        return data


class MiniProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source = "category.name", read_only = True)
    brand_name = serializers.CharField(source = "brand.name", read_only = True)    
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    company_name = serializers.CharField(source = "company.name", read_only = True)

    class Meta:
        model = Product
        fields = ["id",
            "name", "image_url", "price", "category_name", "rating", 
            "rating_count", "reviews", "sku", "brand_name", "description",
            "company_name", "stock"
            ]        

    def get_rating(self, obj):
        from django.db.models import Avg

        if obj.reviews:
            return obj.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or "0"
        return "0"
    
    def get_rating_count(self, obj):

        if obj.reviews:
            return obj.reviews.count() or "0"
        return "0"
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}/{obj.image.url}"
        
        return None


class ProductListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source = "category.name", read_only = True)
    rating = serializers.CharField(source = "get_rating", read_only = True)
    rating_count = serializers.CharField(source = "get_rating_count", read_only = True)
    reviews = serializers.SerializerMethodField()
    company_name = serializers.CharField(source = "company.name", read_only = True)

    class Meta:
        model = Product
        fields = ["id",
            "name", "image_url", "price",
            "category_name", "rating", "rating_count", "reviews", "slug", 
            "sku", "stock", "company_name"
            ]
        
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}/{obj.image.url}"
        
        return None
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all().order_by("-created")[0:5]
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source = "category.name", read_only = True)
    category_slug = serializers.CharField(source = "category.slug", read_only = True)
    sub_category_name = serializers.CharField(source = "sub_category.name", read_only = True)
    sub_category_slug = serializers.CharField(source = "sub_category.slug", read_only = True)
    brand_name = serializers.CharField(source = "brand.name", read_only = True)
    reviews = ReviewSerializer(many=True, read_only=True)
    faqs = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id",
            "name", "image_url", "price", "description", "get_absolute_url", 
            "category_name", "rating", "rating_count", "reviews", "slug", 
            "sku", "stock", "faqs", "category_slug", "brand_name",
            "sub_category_slug", "sub_category_name"
            ]
        
    def get_rating(self, obj):

        if obj.reviews:
            return obj.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or "0"
        return "0"
    
    def get_rating_count(self, obj):

        if obj.reviews:
            return obj.reviews.count() or "0"
        return "0"

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.SITE_URL}/{obj.image.url}"
        
        return None
    
    def get_faqs(self, obj):
        if not obj:
            return None
        
        faqs = Faq.objects.filter(product = obj)[:15]

        serializer = FaqSerializer(faqs, many = True)

        return serializer.data    


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ["id","feature", "id"]


class BulletPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulletPoint
        fields = ["id",
            "id", "bullet_point"
            ]
        

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ["id",
            "id", "heading", "summary"
            ]


class MiniProductDetailSerializer(serializers.ModelSerializer):
    product = MiniProductSerializer()

    company_slug = serializers.CharField(source="company.slug", read_only=True)
    url = serializers.SerializerMethodField()

    company_sub_type = serializers.CharField(source="company.sub_type", read_only=True)

    class Meta:
        model = ProductDetailPage
        fields = ["id",
            "meta_description", "product", "company_slug", 
            "url", "company_sub_type",
            ]
        
    def get_url(self, obj):
        try:
            company_slug = obj.company.slug
            category_slug = obj.product.category.slug
            sub_category_slug = obj.product.sub_category.slug
            slug = obj.slug
        except AttributeError:
            return None

        return f"{company_slug}/{category_slug}/{sub_category_slug}/{slug}"


class DetailListSerializer(serializers.ModelSerializer):
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    product = ProductListSerializer()
    url = serializers.CharField(read_only=True, source="computed_url")

    class Meta:
        model = ProductDetailPage
        fields = ["id", "company_slug",
            "meta_title", "meta_description",
            "product", "slug", "summary",
            "url",            
            ]


class DetailSerializer(serializers.ModelSerializer):    
    name= serializers.CharField(source = "product.name", read_only = True)
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source = "product.category.name", read_only = True)
    category_slug = serializers.CharField(source = "product.category.slug", read_only = True)
    sub_category_name = serializers.CharField(source = "product.sub_category.name", read_only = True)
    sub_category_slug = serializers.CharField(source = "product.sub_category.slug", read_only = True)
    brand_name = serializers.CharField(source = "product.brand.name", read_only = True)
    reviews = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    price = serializers.CharField(source = "product.price", read_only = True)
    sku = serializers.CharField(source = "product.sku", read_only = True)    

    features = FeatureSerializer(many=True)    
    bullet_points = BulletPointSerializer(many=True, read_only=True)    
    timelines = TimelineSerializer(many=True, read_only=True)
    meta_tags = MetaTagSerializer(many=True, read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)
    url = serializers.CharField(source="computed_url", read_only=True)

    company_sub_type = serializers.CharField(source="company.sub_type", read_only=True)    

    class Meta:
        model = ProductDetailPage
        fields = ["id", "name", "image_url", "category_name",
            "meta_title", "meta_description", "sub_category_name",
            "brand_name", "reviews", "faqs", "rating", "rating_count",
            "product", "slug", "summary", "description",
            "features", "bullet_points", "hide_features", "hide_bullets",
            "hide_timeline", "timelines", "meta_tags", 
            "toc", "timeline_title", "hide_support_languages",
            "created", "updated", "company_slug", "url",
            "whatsapp", "external_link", "buy_now_action",
            "category_slug", "sub_category_slug", 
            "company_sub_type", "price", "sku"
            ]   

    def get_reviews(self, obj):        
        reviews_qs = obj.product.reviews.select_related(
            "company", "product", "user"
        )[:12]

        if not reviews_qs:
            return []

        serializer = ReviewSerializer(reviews_qs, many=True)
        return serializer.data
    
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.product.image and hasattr(obj.product.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.product.image.url)
            return f"{settings.SITE_URL}/{obj.product.image.url}"
        
        return None
    
    def get_rating(self, obj):        

        if obj.product.reviews:
            return obj.product.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or "0"
        return "0"
    
    def get_rating_count(self, obj):

        if obj.product.reviews:
            return obj.product.reviews.count() or "0"
        return "0"
    
    def get_faqs(self, obj):
        if not obj.product:
            return None
        
        faqs = Faq.objects.filter(product = obj.product)[:15]

        serializer = FaqSerializer(faqs, many = True)

        return serializer.data  
        

class MultipageFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiPageFeature
        fields = ["id","feature", "id"]


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
        fields = ["id",
            "id", "question", "answer", "slug"
            ]


class MultiPageSerializer(serializers.ModelSerializer):
    products = MiniProductSerializer(many=True, read_only=True)

    features = MultipageFeatureSerializer(many=True)    
    bullet_points = MultipageBulletPointSerializer(many=True, read_only=True)    
    timelines = MultipageTimelineSerializer(many=True, read_only=True)
    faqs = MultipageFaqSerializer(many=True, read_only=True)
    meta_tags = serializers.SerializerMethodField()
    text_editors = TextEditorSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    published = serializers.SerializerMethodField()
    company_slug = serializers.CharField(source = "company.slug", read_only=True)

    class Meta:
        model = MultiPage
        fields = ["id",
            "title", "products", "slug", "meta_description", "summary", "description",
            "features", "bullet_points", "hide_features", "hide_bullets",
            "hide_timeline", "timelines", "meta_tags", "text_editors",
            "toc", "timeline_title", "hide_support_languages",
            "faqs", "rating", "rating_count", "reviews",
            "meta_title", "created", "updated", "published", "url_type",
            "sub_title", "company_slug"
            ]
        
        
    def get_meta_tags(self, obj):
        if not obj.meta_tags:
            return None
        
        meta_tags = obj.meta_tags.all()

        serializer = MiniMetaTagSerializer(meta_tags, many=True)

        return serializer.data
        
    def get_reviews(self, obj):
        if not obj:
            return None
        
        products = obj.products.all()

        reviews = []

        for product in products:
            reviews += product.reviews.all()

        serializer = ReviewSerializer(reviews, many=True)

        return serializer.data
        
    def get_rating(self, obj):
        if not obj:
            return None
        
        products = obj.products.all()

        highest_rating = (max(products, key=lambda p: p.get_rating)).get_rating        

        return highest_rating if highest_rating else 0
    
    def get_rating_count(self, obj):
        if not obj:
            return None
        
        products = obj.products.all()

        highest_rating_count = (max(products, key=lambda p: p.get_rating)).get_rating_count

        return highest_rating_count if highest_rating_count else 0
    
    def get_published(self, obj):
        if not obj:
            return None
        
        return datetime.strftime(obj.created, "%d-%b-%Y")
    

class ProductSubCategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)    
    testimonials = serializers.SerializerMethodField()
    url = serializers.CharField(source="computed_url")
    price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ["id", "faqs",
            "name", "slug", "updated", "image_url", "category_name", 
            "category_slug", "testimonials", "url", "company_name",
            "price", "stock", "description", "starting_title",
            "ending_title", "location_slug", "content",
            "rating"
            ]
        
    read_only_fields = "__all__"

    def get_faqs(self, obj):
        return list(obj.faqs.values("question", "answer"))
        

    def get_price(self, obj):
        if hasattr(obj, "products"):
            product_obj = obj.products.filter(price__isnull = False).first()

            if product_obj and product_obj.price:
                return product_obj.price

        return None
    
    def get_rating(self, obj):
        reviews = Review.objects.filter(company = obj.company, product__sub_category = obj)            

        if reviews:
            return reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0
        
        return 0

        return None
    
    def get_stock(self, obj):
        if hasattr(obj, "products"):
            product_stocks = list(obj.products.filter(stock__isnull = False).values_list("stock", flat=True))

            return sum(product_stocks)

        return None
    
    def get_testimonials(self, obj):

        reviews = Review.objects.filter(company = obj.company, product__sub_category = obj)

        serializer = ReviewSerializer(reviews, many=True)

        return serializer.data

    def get_image_url(self, obj):
        request = self.context.get('request')

        product = obj.products.filter(image__isnull = False).exclude(image = "").order_by("created").first()

        if product and product.image and hasattr(product.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(product.image.url)
            return f"{settings.SITE_URL}{product.image.url}"
        
        return None


class MiniProductCategorySerializer(serializers.ModelSerializer):
    sub_categories = ProductSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id",
            "name", "slug", "sub_categories",
            ]

    read_only_fields = "__all__"


class HomeProductCategorySerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    # sub_categories = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id",
            "details", "name", "slug", "testimonials",
            "updated", "image_url"
            ]

    read_only_fields = "__all__"

    def get_details(self, obj):
        if not obj:
            return None
        
        details = ProductDetailPage.objects.filter(product__category = obj).select_related(
            "company", "product"
        )[:16]
        
        serializer = DetailListSerializer(details, many=True)

        return serializer.data
    
    # def get_sub_categories(self, obj):
    #     if not obj:
    #         return None
        
    #     sub_categories = SubCategory.objects.filter(category = obj)

    #     return ProductSubCategorySerializer(sub_categories, many=True).data
    
    def get_testimonials(self, obj):

        reviews = Review.objects.filter(company = obj.company, product__category = obj)

        serializer = ReviewSerializer(reviews, many=True)

        return serializer.data
    
    def get_image_url(self, obj):
        request = self.context.get('request')

        product = obj.products.filter(image__isnull = False).exclude(image = "").order_by("created").first()

        if product and product.image and hasattr(product.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(product.image.url)
            return f"{settings.SITE_URL}{product.image.url}"
        
        return None


class ProductCategorySerializer(serializers.ModelSerializer):    
    testimonials = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id",
            "name", "slug", "testimonials",
            "updated", "image_url"
            ]

    read_only_fields = "__all__"    
    
    def get_testimonials(self, obj):

        reviews = Review.objects.filter(company = obj.company, product__category = obj)

        serializer = ReviewSerializer(reviews, many=True)

        return serializer.data
    
    def get_image_url(self, obj):
        request = self.context.get('request')

        product = obj.products.filter(image__isnull = False).exclude(image = "").order_by("created").first()

        if product and product.image and hasattr(product.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(product.image.url)
            return f"{settings.SITE_URL}{product.image.url}"
        
        return None
    

class EnquirySerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
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
        fields = ["id","company", "name", "phone", "email", "product", "state"]
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
            self.fields['product'].queryset = Product.objects.filter(
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