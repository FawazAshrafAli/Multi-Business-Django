from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from datetime import datetime
from django.db.models import Avg

from company.models import Company
from locations.models import UniqueState
from base.models import MetaTag

class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug = slug).exclude(pk = self.pk).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_category"
        ordering = ["name"]

    @property
    def sub_categories(self):
        return SubCategory.objects.filter(category = self).values("name", "slug")
    
    @property
    def detail_pages(self):
        return ProductDetailPage.objects.filter(product__category = self).values("product__name", "slug")
    

class SubCategoryFaq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="sub_category_faqs")
    sub_category_slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    question = models.CharField(max_length=255)
    answer = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.sub_category_slug}")
            slug = base_slug

            count = 1
            while SubCategoryFaq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sub_category_slug}-{self.company.name}"
    
    class Meta:
        db_table = "sub_category_faqs"
        ordering = ["created"]


class SubCategory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_sub_categories")

    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="sub_categories")
    description = models.TextField(null=True, blank=True)

    starting_title = models.CharField(max_length=255, null=True, blank=True)
    ending_title = models.CharField(max_length=255, null=True, blank=True)

    location_slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    content = models.TextField(blank=True, null=True)

    faqs = models.ManyToManyField(SubCategoryFaq)
    hide_faqs = models.BooleanField(default=False)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_sub_category"
        ordering = ["name"]

    @property
    def computed_url(self):
        return f"{self.company.slug}/{self.category.slug}/{self.slug}"


class Brand(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_brand"
        ordering = ["name"]


class Size(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    standard = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.category.name}")
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_sizes"
        ordering = ["name"]


class Color(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    hexa = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.hexa}")
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def str(self):
        return self.name

    class Meta:
        db_table = "product_colors"
        ordering = ["name"]
        

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.CharField(max_length=20)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products")
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True, null=True)    
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    # Additional fields
    colors = models.ManyToManyField(Color)
    sizes = models.ManyToManyField(Size)
    weight = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    length = models.CharField(max_length=50, blank=True, null=True)
    width = models.CharField(max_length=50, blank=True, null=True)
    height = models.CharField(max_length=50, blank=True, null=True)
    unit = models.CharField(max_length=50, null=True, blank=True)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    @property
    def color_slugs(self):
        return self.colors.values_list("slug", flat=True)

    @property
    def get_colors(self):
        colors = self.colors.all()
        if colors and len(colors) > 0:
            color_list = []
            for color in colors:
                color_list.append(f"<div style='height: 15px; width: 15px; border: 1px solid black; background-color: {color.hexa};'></div>&nbsp;{color.name}")
            return ',&nbsp;'.join(color_list)
        return None
    
    @property
    def size_slugs(self):
        return self.sizes.values_list("slug", flat=True)
    
    @property
    def get_sizes(self):
        sizes = self.sizes.all()
        if sizes and len(sizes) > 0:
            sizes_list = []
            for size in sizes:
                if size.standard:
                    sizes_list.append(f"{size.name} ({size.standard})")
                else:
                    sizes_list.append(size.name)
            return ',&nbsp;'.join(sizes_list)
        return None
    
    @property
    def get_dimension(self):
        if self.length and self.width and self.height:
            return f"{self.length} {self.unit} x {self.width} {self.unit} x {self.height} {self.unit}"
        
        elif self.length and self.width:
            return f"{self.length} {self.unit} x {self.width} {self.unit}"
        
        return None
    
    @property
    def get_weight(self):
        try:
            if int(self.weight) == 0:
                return None
        except (ValueError, TypeError):
            return self.weight
        
    def str(self):
        return self.name

    class Meta:
        db_table = "products"
        ordering = ["name"]

    @property
    def get_reviews(self):
        return self.reviews.all().order_by("-created")

    @property
    def get_rating(self):
        if self.reviews:
            return self.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0
        return "0"

    @property
    def get_rating_count(self):
        if self.reviews:
            return self.reviews.count() or 0
        return "0"
    
    @property
    def get_absolute_url(self):
        return f'/products/{self.slug}'
    
    @property
    def blogs(self):
        from blog.models import Blog
        return Blog.objects.filter(product = self, is_published=True)
    

class Faq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_faqs")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="faqs")

    question = models.TextField()
    answer = models.TextField()
    dynamic_place_rendering = models.BooleanField(default=False)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.product.name)
            slug = base_slug

            count = 1
            while Faq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_faqs"
        ordering = ["-created"]


class Review(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="review_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    review_by = models.TextField(null=True, blank=True)

    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)

    order = models.PositiveIntegerField(default=0)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            user = self.user.username if not self.review_by else self.review_by            

            base_slug = slugify(f"{self.product}-{user}")

            slug = base_slug
            count = 1

            while Review.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        user = self.user.username if not self.review_by else self.review_by
        return f"{self.company.name}-{self.product}-{user}"

    class Meta:
        db_table = "reviews"
        ordering = ["created"] 

    @property
    def computed_created_date(self):
        if not self.created:
            return None
        return datetime.strftime(self.created, "%b %d, %Y")
    
    @property
    def get_avg_rating(self):
        return (
            Review.objects.filter(company=self.company)
            .aggregate(avg=Avg("rating"))
            .get("avg") or 0 
        )

class Enquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_enquiry_company")

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="product_enquiry_state")

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.product.name}-{self.email}")
            slug = base_slug

            count = 1
            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}-{self.email}"
    
    class Meta:
        db_table = "product_enquiries"
        ordering = ["-created"]    


class Feature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_feature_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    feature = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_features"
        ordering = ["created"]


class BulletPoint(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_bullet_points_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_bullet_points"
        ordering = ["created"]

    
class Timeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_timeline_company")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_timelines"
        ordering = ["created"]


class ProductDetailPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_details")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    summary = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    meta_title = models.CharField(max_length=255)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

    features = models.ManyToManyField(Feature)
    
    bullet_points = models.ManyToManyField(BulletPoint)
    
    # Timeline
    timeline_title = models.CharField(max_length=255, null=True, blank=True)
    timelines = models.ManyToManyField(Timeline)

    hide_features = models.BooleanField(default=False)    
    hide_bullets = models.BooleanField(default=False)    
    hide_timeline = models.BooleanField(default=False)

    hide_support_languages = models.BooleanField(default=False)

    buy_now_action = models.CharField(max_length=50, default="whatsapp")
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    external_link = models.URLField(max_length=500, blank=True, null=True)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.product.name} - {self.company.name}"

        if not self.slug:
            base_slug = slugify(self.product.name)
            slug = base_slug
            count = 1

            while ProductDetailPage.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_details"
        ordering = ["created"]
    
    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
    
    @property
    def toc(self):
        options = {            
            self.timeline_title: self.hide_timeline
        }

        toc = [title for title, hidden in options.items() if not hidden]
        toc += ["FAQs", "Tags", "Articles"]

        return toc
    
    @property
    def image_count(self):
        if self.product.image:
            return 1
        
        return 0

    @property
    def computed_url(self):
        return f"{self.company.slug}/{self.product.category.slug}/{self.product.sub_category.slug}/{self.slug}"


class MultiPageFeature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_feature")
    title = models.CharField(max_length=255)

    feature = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_features"
        ordering = ["created"]


class MultiPageBulletPoint(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_bullets")
    title = models.CharField(max_length=255)

    bullet_point = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_bullet_points"
        ordering = ["created"]


class MultiPageTimeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_timeline")
    title = models.CharField(max_length=255)

    heading = models.CharField(max_length=255)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.product.name}"
    
    class Meta:
        db_table = "product_multipage_timelines"
        ordering = ["created"]


class TextEditor(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_text_editors")
    title = models.CharField(max_length = 255)

    text_editor_title = models.CharField(max_length=255)
    content = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.text_editor_title}")
            slug = base_slug

            count = 1
            while TextEditor.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "product_text_editors"
        ordering = ["created"]



class MultiPageFaq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_product_multipage_faq")
    title = models.CharField(max_length=255)

    question = models.CharField(max_length=255)
    answer = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.company.name}"
    
    class Meta:
        db_table = "product_multipage_faqs"
        ordering = ["created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug

            count = 1
            while MultiPageFaq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)


class MultiPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_multipages")

    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length = 255, blank=True, null=True)

    products = models.ManyToManyField(Product)

    summary = models.TextField(null=True, blank=True)
    description = RichTextField()

    meta_title = models.CharField(max_length=255)
    meta_tags = models.ManyToManyField(MetaTag, related_name="meta_tag_of_multipage")
    meta_description = models.TextField()

    url_type = models.CharField(max_length=50, default="slug_filtered")

    product_region = models.CharField(max_length=255, default="all")
    available_states = models.ManyToManyField(UniqueState, related_name="product_multipages")

    features = models.ManyToManyField(MultiPageFeature)    

    # Bullet Point
    bullet_title = models.CharField(max_length=255, null=True, blank=True)
    bullet_points = models.ManyToManyField(MultiPageBulletPoint)

    # Timeline
    timeline_title = models.CharField(max_length=255, null=True, blank=True)
    timelines = models.ManyToManyField(MultiPageTimeline)

    # Faqs
    faqs = models.ManyToManyField(MultiPageFaq)

    text_editors = models.ManyToManyField(TextEditor)

    hide_features = models.BooleanField(default=False)    
    hide_bullets = models.BooleanField(default=False)    
    hide_timeline = models.BooleanField(default=False)
    hide_faqs = models.BooleanField(default=False)

    hide_support_languages = models.BooleanField(default=False)

    buy_now_action = models.CharField(max_length=50, default="whatsapp")
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    external_link = models.URLField(max_length=500, blank=True, null=True)

    home_footer_visibility = models.BooleanField(default=False)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.title} - {self.company.name}"

        if not self.home_footer_visibility and not MultiPage.objects.exclude(pk=self.pk).filter(company = self.company, home_footer_visibility=True).exists():
            self.home_footer_visibility = True

        base_slug = slugify(self.title)
        slug = base_slug
        count = 1

        while MultiPage.objects.filter(slug = slug).exclude(pk = self.pk).exists():
            slug = f"{base_slug}{count}"
            count += 1

        if self.url_type != "slug_filtered":
            slug = slug.replace("-in-place_name", "").replace("-in-district_name", "").replace("-in-state_name", "").replace("-place_name", "").replace("-district_name", "").replace("-state_name", "")

        self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "product_multipages"
        ordering = ["created"]
    
    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
    
    @property
    def toc(self):
        options = {            
            self.timeline_title: self.hide_timeline,
            "FAQs": self.hide_faqs
        }

        text_editor_title_list = self.text_editors.values_list("text_editor_title", flat=True)
        toc = [title for title, hidden in options.items() if not hidden]

        toc += ["Tags"]
        toc += text_editor_title_list

        return toc

    @property
    def image_count(self):
        if self.products.count() > 0:
            return len([product.image for product in self.products.all() if product.image])
        
        return 0