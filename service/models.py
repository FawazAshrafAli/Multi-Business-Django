from django.db import models
from django.utils.text import slugify
from datetime import datetime
from ckeditor.fields import RichTextField

from django.db.models import Avg

from company.models import Company
from locations.models import UniqueState
from base.models import MetaTag

class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_category_company")

    name = models.CharField(max_length=255)
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


    def __str__(self):
        return f"{self.name}-{self.company.name}"

    class Meta:
        db_table = "service_category"
        ordering = ["name"]

    @property
    def sub_categories(self):
        return SubCategory.objects.filter(category = self).values("name", "slug")
    
    @property
    def detail_pages(self):
        return ServiceDetail.objects.filter(service__category = self).values("service__name", "slug")
    

class SubCategoryFaq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
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
        db_table = "service_sub_faqs"
        ordering = ["created"]


class SubCategory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_sub_categories")

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
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
            while SubCategory.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name}-{self.category.name}-{self.company.name}"

    class Meta:
        db_table = "service_sub_category"
        ordering = ["name"]

    @property
    def computed_url(self):
        return f"{self.company.slug}/{self.category.slug}/{self.slug}"


class Service(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="services")

    image = models.ImageField(upload_to="services/", null=True, blank=True)
    name = models.CharField(max_length=255)    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services")
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="services")
    description = models.TextField(null=True, blank=True)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    price = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug

            count = 1
            while Service.objects.filter(slug = slug).exists():
                if Service.objects.filter(slug = slug).first().pk == self.pk:
                    break

                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.company.name}"
    
    class Meta:
        db_table = "services"
        ordering = ["name"]

    @property
    def get_image_name(self):
        if self.image:
            return self.image.name.replace('services/', '')
        
        return None    

class Feature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_feature_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    feature = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_features"
        ordering = ["created"]


class VerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_vertical_bullet_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255, null=True, blank=True)
    sub_heading = models.CharField(max_length=255, null=True, blank=True)

    bullet = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_vertical_bullets"
        ordering = ["created"]


class VerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_vertical_tab_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=255, null=True, blank=True)
    sub_heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(VerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_vertical_tabs"
        ordering = ["created"]


class HorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_horizontal_bullet_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255, null=True, blank=True)

    bullet = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_horizontal_bullets"
        ordering = ["created"]


class HorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_horizontal_tab_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(HorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_horizontal_tabs"
        ordering = ["created"]


class TableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_table_data_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255)
    data = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_table_data"
        ordering = ["created"]


class Table(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_table_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255)
    datas = models.ManyToManyField(TableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_table"
        ordering = ["created"]    


class BulletPoints(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_bullet_points_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_bullet_points"
        ordering = ["created"]

    
class Timeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_timeline_company")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_timelines"
        ordering = ["created"]


class ServiceDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_details")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    summary = models.TextField()
    description = models.TextField(null=True, blank=True)

    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()

    features = models.ManyToManyField(Feature)

    meta_tags = models.ManyToManyField(MetaTag, related_name="meta_tags_of_detail_page")

    # Verical Tab
    vertical_title = models.CharField(max_length=255, null=True, blank=True)
    vertical_tabs = models.ManyToManyField(VerticalTab)

    # Horizontal Tab
    horizontal_title = models.CharField(max_length=255, null=True, blank=True)
    horizontal_tabs = models.ManyToManyField(HorizontalTab)

    # Table
    table_title = models.CharField(max_length=255, null=True, blank=True)
    tables = models.ManyToManyField(Table)

    # Bullet Point
    bullet_title = models.CharField(max_length=255, null=True, blank=True)
    bullet_points = models.ManyToManyField(BulletPoints)

    # Timeline
    timeline_title = models.CharField(max_length=255, null=True, blank=True)
    timelines = models.ManyToManyField(Timeline)

    hide_features = models.BooleanField(default=False)
    hide_vertical_tab = models.BooleanField(default=False)
    hide_horizontal_tab = models.BooleanField(default=False)
    hide_table = models.BooleanField(default=False)
    hide_bullets = models.BooleanField(default=False)
    hide_timeline = models.BooleanField(default=False)

    hide_support_languages = models.BooleanField(default=False)    

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.service.name} - {self.company.name}"        

        if not self.slug:
            base_slug = slugify(self.service.name)
            slug = base_slug
            count = 1

            while ServiceDetail.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"  
    
    class Meta:
        db_table = "service_details"
        ordering = ["created"]

    @property
    def computed_url(self):
        return f"{self.company.slug}/{self.service.category.slug}/{self.service.sub_category.slug}/{self.slug}"

    @property
    def get_data(self):        
        rows = []
        tables = self.tables.all()

        for table in tables:
            data = [data.data for data in table.datas.all()]
            rows.append(data)

        transposed_data = list(map(list, zip(*rows)))

        return transposed_data
    
    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
    
    @property
    def toc(self):
        options = {
            self.vertical_title: self.hide_vertical_tab,
            self.horizontal_title: self.hide_horizontal_tab,
            self.table_title: self.hide_table,
            self.bullet_title: self.hide_bullets,            
            self.timeline_title: self.hide_timeline
        }

        toc = [title for title, hidden in options.items() if not hidden]
        toc += ["FAQs", "Tags", "Services", "Articles"]

        return toc
    
    @property
    def published(self):
        if self.created:
            return datetime.strftime(self.created, "%Y-%m-%d")
        return None
    
    @property
    def modified(self):
        if self.updated:
            return datetime.strftime(self.updated, "%Y-%m-%d")
        return None

    @property
    def image_count(self):
        if self.service.image:
            return 1
        
        return 0

class Enquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_enquiry_company")

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.service.name}-{self.email}")
            slug = base_slug

            count = 1
            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}-{self.email}"
    
    class Meta:
        db_table = "service_enquiries"
        ordering = ["-created"]


class Faq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_faqs")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="faqs")

    question = models.TextField()
    answer = models.TextField()
    dynamic_place_rendering = models.BooleanField(default=False)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.question)
            slug = base_slug

            count = 1
            while Faq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_faqs"
        ordering = ["-created"]


class MultiPageFeature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_feature")
    title = models.CharField(max_length = 255)

    feature = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_features"
        ordering = ["created"]


class MultiPageVerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_vertical_bullet")
    title = models.CharField(max_length = 255)

    heading = models.CharField(max_length=255, null=True, blank=True)
    sub_heading = models.CharField(max_length=255, null=True, blank=True)

    bullet = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_vertical_bullets"
        ordering = ["created"]
    

class MultiPageVerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_vertical_tab")
    title = models.CharField(max_length = 255)
    
    heading = models.CharField(max_length=255, null=True, blank=True)
    sub_heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageVerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_vertical_tabs"
        ordering = ["created"]


class MultiPageHorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_horizontal_bullet")
    title = models.CharField(max_length = 255)

    heading = models.CharField(max_length=255, null=True, blank=True)

    bullet = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_horizontal_bullets"
        ordering = ["created"]


class MultiPageHorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_horizontal_tab")
    title = models.CharField(max_length = 255)

    heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageHorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_horizontal_tabs"
        ordering = ["created"]

class MultiPageTableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_table_data")
    title = models.CharField(max_length = 255)

    heading = models.CharField(max_length=255)
    data = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_table_data"
        ordering = ["created"]


class MultiPageTable(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_table")
    title = models.CharField(max_length = 255)

    heading = models.CharField(max_length=255)
    datas = models.ManyToManyField(MultiPageTableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_table"
        ordering = ["created"]    


class MultiPageBulletPoint(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_bullets")
    title = models.CharField(max_length = 255)

    bullet_point = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_bullet_points"
        ordering = ["created"]


class MultiPageTimeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_of_service_multipage_timeline")
    title = models.CharField(max_length = 255)

    heading = models.CharField(max_length=255)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipage_timelines"
        ordering = ["created"]


class TextEditor(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_text_editors")
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
        db_table = "service_text_editors"
        ordering = ["created"]


class MultiPageFaq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_multi_faqs")
    title = models.CharField(max_length = 255)

    question = models.CharField(max_length=255)
    answer = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}-{self.title}"
    
    class Meta:
        db_table = "service_multipage_faqs"
        ordering = ["created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.question)
            slug = base_slug

            count = 1
            while MultiPageFaq.objects.filter(slug = slug).exclude(pk = self.pk).exists():
                slug = f"{base_slug}{count}"

                count += 1

            self.slug = slug

        super().save(*args, **kwargs)


class MultiPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="service_multipages")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="multipages")

    title = models.CharField(max_length = 255)
    sub_title = models.CharField(max_length = 255, blank=True, null=True)

    summary = models.TextField(null=True, blank=True)
    description = RichTextField()

    meta_title = models.CharField(max_length=255)
    meta_tags = models.ManyToManyField(MetaTag, related_name="meta_tags_of_multi_page")
    meta_description = models.TextField()

    url_type = models.CharField(max_length=50, default="slug_filtered")

    service_region = models.CharField(max_length=255, default="all")
    available_states = models.ManyToManyField(UniqueState, related_name="service_multipages")

    slider_services = models.ManyToManyField(ServiceDetail)

    features = models.ManyToManyField(MultiPageFeature)

    # Verical Tab
    vertical_title = models.CharField(max_length=255, null=True, blank=True)
    vertical_tabs = models.ManyToManyField(MultiPageVerticalTab)

    # Horizontal Tab
    horizontal_title = models.CharField(max_length=255, null=True, blank=True)
    horizontal_tabs = models.ManyToManyField(MultiPageHorizontalTab)

    # Table
    table_title = models.CharField(max_length=255, null=True, blank=True)
    tables = models.ManyToManyField(MultiPageTable)

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
    hide_vertical_tab = models.BooleanField(default=False)
    hide_horizontal_tab = models.BooleanField(default=False)
    hide_table = models.BooleanField(default=False)
    hide_bullets = models.BooleanField(default=False)    
    hide_timeline = models.BooleanField(default=False)
    hide_faqs = models.BooleanField(default=False)

    hide_support_languages = models.BooleanField(default=False)
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
        return f"{self.company.name}-{self.service.name}"
    
    class Meta:
        db_table = "service_multipages"
        ordering = ["created"]

    @property
    def slider_service_category_slug(self):
        if self.slider_services.count() > 0:
            first_slider_service_detail = self.slider_services.first()
            return first_slider_service_detail.service.category.slug
        
        return None
    
    @property
    def slider_service_sub_category_slug(self):
        if self.slider_services.count() > 0:
            first_slider_service_detail = self.slider_services.first()
            return first_slider_service_detail.service.sub_category.slug
        
        return None

    @property
    def get_data(self):        
        rows = []
        tables = self.tables.all()

        for table in tables:
            data = [data.data for data in table.datas.all()]
            rows.append(data)

        transposed_data = list(map(list, zip(*rows)))

        return transposed_data
    
    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
    
    @property
    def toc(self):
        options = {
            self.vertical_title: self.hide_vertical_tab,
            self.horizontal_title: self.hide_horizontal_tab,
            self.table_title: self.hide_table,
            self.bullet_title: self.hide_bullets,
            self.timeline_title: self.hide_timeline
        }

        text_editor_title_list = self.text_editors.values_list("text_editor_title", flat=True)
        toc = [title for title, hidden in options.items() if not hidden]

        toc += ["FAQs", "Tags", "Services"]
        toc += text_editor_title_list

        return toc
    
    @property
    def published(self):
        if self.created:
            return datetime.strftime(self.created, "%Y-%m-%d")
        return None
    
    @property
    def modified(self):
        if self.updated:
            return datetime.strftime(self.updated, "%Y-%m-%d")
        return None
    
    @property
    def rating(self):
        from company.models import Testimonial
        testimonials = Testimonial.objects.filter(company = self.company).values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

    @property
    def rating_count(self):
        from company.models import Testimonial
        return Testimonial.objects.filter(company = self.company).count()
    
    @property
    def image_count(self):
        if self.service.image:
            return 1
        
        return 0