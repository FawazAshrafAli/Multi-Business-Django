from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.db.models import Avg
from django.db import transaction

from locations.models import UniquePlace, UniqueState
from base.models import MetaTag
from django.db import IntegrityError

class CompanyType(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while CompanyType.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "company_type"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    @property
    def companies(self):
        return Company.objects.filter(type = self).values("name", "slug").order_by("name")
    
    @property
    def categories(self):
        from educational.models import Program
        from product.models import Category as ProductCategory
        from registration.models import RegistrationType
        from service.models import Category as ServiceCategory

        current_type = self.name
        Category = None

        if current_type == "Education":
            Category = Program

        elif current_type == "Product":
            Category = ProductCategory

        elif current_type == "Registration":
            Category = RegistrationType

        elif current_type == "Service":
            Category = ServiceCategory

        if Category:
            categories = Category.objects.all().order_by("name")

            return [{"name": category.name, "slug": category.slug, "sub_categories": category.sub_categories, "detail_pages": category.detail_pages if hasattr(category, "detail_pages") else None} for category in categories]

        return None
    
    # @property
    # def companies(self):
    #     return Company.objects.filter(type = self).order_by("name")
    

class Company(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(CompanyType, on_delete=models.CASCADE, related_name="companies")
    sub_type = models.CharField(max_length=250)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)
    favicon = models.ImageField(upload_to="company_favicon/", null=True, blank=True)
    logo = models.ImageField(upload_to="company_logo/", null=True, blank=True)
    phone1 = models.CharField(max_length=50)
    phone2 = models.CharField(max_length=50)
    whatsapp = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)

    summary = models.TextField()
    description = RichTextField(null=True, blank=True)

    add_on_company_types = models.ManyToManyField(CompanyType, related_name="add_on_companies")

    meta_title = models.CharField(max_length=255)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

    footer_content = RichTextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.meta_title:
            self.meta_title = f"Home - {self.name}"

        if not self.slug:
            base_slug = slugify(self.sub_type)
            slug = base_slug
            count = 1
            while CompanyType.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "company"
        ordering = ["name"]

    @property
    def get_place_name(self):
        place_names = list(self.contacts.values_list("place__name", flat=True))

        if place_names:
            return place_names[0]
        
        return None
    
    @property
    def get_district_name(self):
        district_names = list(self.contacts.values_list("district__name", flat=True))

        if district_names:
            return district_names[0]
        
        return None
    
    @property
    def get_state_name(self):
        state_names = list(self.contacts.values_list("state__name", flat=True))

        if state_names:
            return state_names[0]
        
        return None
    
    @property
    def get_pincode(self):
        pincodes = list(self.contacts.values_list("pincode", flat=True))

        if pincodes:
            return pincodes[0]
        
        return None

    @property
    def get_client_slider_heading(self):
        client_slider_obj = ClientSlider.objects.filter(company = self).first()

        if client_slider_obj and hasattr(client_slider_obj, "heading"):
            return client_slider_obj.heading
            
        return None 

    @property
    def get_categories(self):
        from educational.models import Program
        from product.models import Category as ProductCategory
        from registration.models import RegistrationType
        from service.models import Category as ServiceCategory

        company_type = self.type.name
        Category = None

        if company_type == "Education":
            Category = Program

        elif company_type == "Product":
            Category = ProductCategory

        elif company_type == "Registration":
            Category = RegistrationType

        elif company_type == "Service":
            Category = ServiceCategory

        if Category:
            return list(Category.objects.filter(company = self).values("name", "slug").order_by("name"))

        return None


    @property
    def get_meta_tags(self):
        if not self.meta_tags:
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
    
    @property
    def rating(self):
        TestimonialModel = Testimonial
        if self.type == "Education":
            from educational.models import Testimonial as CourseTestimonial

            TestimonialModel = CourseTestimonial

        testimonials = TestimonialModel.objects.filter(company = self).values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

    @property
    def get_rating(self):
        TestimonialModel = Testimonial
        if self.type == "Education":
            from educational.models import Testimonial as CourseTestimonial

            TestimonialModel = CourseTestimonial

        testimonials = TestimonialModel.objects.filter(company = self).values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0
    
    @property
    def get_absolute_url(self):
        return f'https://bzindia.in/{self.slug}'

    @property
    def get_blogs(self):
        return self.blogs.filter(is_published = True)
    
    @property
    def faqs(self):
        from custom_pages.models import FAQ

        return FAQ.objects.filter(company = self)
    
    @property
    def get_price_range(self):       
        if self.type.name == "Education":
            course = self.courses.filter(price__isnull = False).first()
            return course.price
        
        elif self.type.name == "Service":
            service = self.services.filter(price__isnull = False).first()
            return service.price
        
        elif self.type.name == "Registration":
            registration = self.registrations.filter(price__isnull = False).first()
            return registration.price
        
        elif self.type.name == "Product":
            product = self.products.filter(price__isnull = False).first()
            return product.price
            
        return None
    
    @property
    def clients(self):
        if self.type.name != "Education":
            return Client.objects.filter(company = self)
        
        return []

    @property
    def add_on_types(self):
        return [company_type.name for company_type in self.add_on_company_types.all()]
    

class ClientSlider(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="client_slider_headings")
    heading = models.CharField(max_length=255)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.slug:
                base_slug = slugify(self.heading)

                slug = base_slug
                count = 1

                while ClientSlider.objects.filter(slug = slug).exists():
                    slug = f"{base_slug}{count}"
                    count += 1

                self.slug = slug

            ClientSlider.objects.filter(company=self.company).exclude(pk=self.pk).delete()

            try:
                super().save(*args, **kwargs)
            except IntegrityError:
                # regenerate slug and retry once
                self.slug = f"{base_slug}{count}"
                super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.heading}"

    class Meta:
        db_table = "client_sliders"
        ordering = ["heading"]


class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="clients")

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="clients/")
    url = models.URLField(max_length=220, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            slug = base_slug
            count = 1

            while Client.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.name}"

    class Meta:
        db_table = "clients"
        ordering = ["name"]


class Testimonial(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="testimonials")

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="testimonials/")

    client_company = models.CharField(max_length=255)
    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE, related_name="testimonial_place")

    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)

    order = models.PositiveIntegerField(default=0)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.client_company}-{self.place.name}")

            slug = base_slug
            count = 1

            while Testimonial.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.name}-{self.client_company}-{self.place.name}"

    class Meta:
        db_table = "testimonials"
        ordering = ["created"]

    @property
    def get_image_name(self):
        if self.image:
            return f"{self.image.name}".replace('testimonials/', '')
        return None
    
    
class ContactEnquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contact_enquiry_company")

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="contact_state")
    message = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.email)
            slug = base_slug

            count = 1
            while ContactEnquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.email}"
    
    class Meta:
        db_table = "contact_enquiries"
        ordering = ["-created"]


class Banner(models.Model):
    from company.models import Company

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="banners")

    image = models.ImageField(upload_to="banners/")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=200)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table="banners"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.company.name}-banner-{self.pk}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"banner-{self.title}")
            slug = base_slug

            count = 0

            while Banner.objects.filter(slug = slug):
                slug = f"{base_slug}{count}"

                count += 1

            self.slug = slug

        super().save(*args, **kwargs)