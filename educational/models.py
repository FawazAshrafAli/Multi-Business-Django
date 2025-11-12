from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.db.models import Avg
from django.utils import timezone
from datetime import datetime   

from company.models import Company

from locations.models import UniquePlace, UniqueState
from base.models import MetaTag


class Program(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="programs")

    name = models.CharField(max_length=255)    

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1

            while Program.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        db_table = "course_programs"
        ordering = ["name"]

    @property
    def sub_categories(self):
        return Specialization.objects.filter(program = self).values("name", "slug")

    @property
    def courses(self):
        return Course.objects.filter(program = self)    


class Specialization(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="specializations")

    name = models.CharField(max_length=255)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1

            while Specialization.objects.filter(slug = slug).exclude(pk = self.pk).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "specializations"
        ordering = ["name"]

    @property
    def computed_url(self):
        return f"{self.company.slug}/{self.program.slug}/{self.slug}"


class Course(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="courses")

    image = models.ImageField(upload_to="course/", null=True, blank=True)
    name = models.CharField(max_length=255)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name = "courses")
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    mode = models.CharField(max_length=150)
    duration = models.CharField(blank=True, null=True, max_length=20)
    price = models.CharField(blank=True, null=True, max_length=20)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    subtitles = models.TextField(null=True, blank=True)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1

            while Specialization.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.program} in {self.specialization}"
    
    class Meta:
        db_table = "courses"
        ordering = ["name"]

    @property
    def get_image_name(self):
        if self.image:
            return self.image.name.replace('course/', '')
        return None
    

    @property
    def description(self):
        detail_page = CourseDetail.objects.filter(course = self).first()

        if detail_page:
            return detail_page.summary
        
        return None
        
    @property
    def rating(self):
        testimonials = Testimonial.objects.filter(course = self).values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

    @property
    def rating_count(self):
        return Testimonial.objects.filter(course = self).count()
    
    @property
    def starting_date(self):
        today = timezone.now().date()

        starting_year = today.year
        starting_month = 6
        starting_day = 1

        if today.month >= 6:
            starting_year += 1
            starting_month = 1

        row_starting_date = f"{starting_day}/{starting_month}/{starting_year}"

        starting_date = datetime.strptime(row_starting_date, "%d/%m/%Y")

        return starting_date
    
    @property
    def ending_date(self):

        return ""

class Feature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    feature = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "features"
        ordering = ["created"]


class VerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255, null=True, blank=True)
    sub_heading = models.CharField(max_length=255, null=True, blank=True)

    bullet = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "vertical_bullets"
        ordering = ["created"]
    

class VerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    heading = models.CharField(max_length=255, null=True, blank=True)
    sub_heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(VerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "vertical_tabs"
        ordering = ["created"]


class HorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255, null=True, blank=True)

    bullet = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "horizontal_bullets"
        ordering = ["created"]


class HorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(HorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "horizontal_tabs"
        ordering = ["created"]

class TableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255)
    data = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "table_data"
        ordering = ["created"]


class Table(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255)
    datas = models.ManyToManyField(TableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "table"
        ordering = ["created"]



class BulletPoints(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    bullet_point = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "bullet_points"
        ordering = ["created"]


class Timeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    heading = models.CharField(max_length=255)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "timelines"
        ordering = ["created"]


class CourseDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name = "course_details")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    summary = models.TextField()
    description = RichTextField()

    meta_title = models.CharField(max_length=255)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

    features = models.ManyToManyField(Feature)

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
            self.meta_title = f"{self.course.name} - {self.company.name}"

        if not self.slug:
            base_slug = slugify(self.course.name)
            slug = base_slug
            count = 1

            while CourseDetail.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "course_details"
        ordering = ["created"]

    @property
    def computed_url(self):
        return f"{self.company.slug}/{self.course.program.slug}/{self.course.specialization.slug}/{self.slug}"

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
        toc += ["FAQs", "Tags", "Courses", "Articles"]

        return toc
    
    @property
    def blogs(self):
        from blog.models import Blog

        return Blog.objects.filter(course = self.course, company = self.company)
    
    @property
    def faqs(self):        
        return Faq.objects.filter(course = self.course, company = self.company)
    
    @property
    def testimonials(self):
        return Testimonial.objects.filter(course = self.course, company = self.company)
    
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
        if self.course.image:
            return 1
        
        return 0
    
    @property
    def get_rating(self):
        testimonials = self.course.course_testimonials.values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

class Enquiry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="course_enquiry_company")

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="course_state")

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.course.name}-{self.email}")
            slug = base_slug

            count = 1
            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.course.name}-{self.email}"
    
    class Meta:
        db_table = "course_enquiries"
        ordering = ["-created"]


class Faq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="faq_company")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    dynamic_place_rendering = models.BooleanField(default=False)

    question = models.TextField()
    answer = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.question}")
            slug = base_slug

            count = 1
            while Faq.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "course_faqs"
        ordering = ["-created"]


class Testimonial(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="student_testimonials/")

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_testimonials")
    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE)

    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)

    order = models.PositiveIntegerField(default=0)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.course.name}-{self.place.name}")

            slug = base_slug
            count = 1

            while Testimonial.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company.name}-{self.name}-{self.course.name}-{self.place.name}"

    class Meta:
        db_table = "student_testimonials"
        ordering = ["created"]

    @property
    def get_image_name(self):
        if self.image:
            return f"{self.image.name}".replace('student_testimonials/', '')
        return None
    
    @property
    def rating_range(self):
        return range(5)
    

class MultiPageFeature(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    feature = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_features"
        ordering = ["created"]


class MultiPageVerticalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    heading = models.CharField(max_length=255, null=True, blank=True)
    sub_heading = models.CharField(max_length=255, null=True, blank=True)

    bullet = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_vertical_bullets"
        ordering = ["created"]
    

class MultiPageVerticalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)
    
    heading = models.CharField(max_length=255, null=True, blank=True)
    sub_heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageVerticalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_vertical_tabs"
        ordering = ["created"]


class MultiPageHorizontalBullet(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    heading = models.CharField(max_length=255, null=True, blank=True)

    bullet = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_horizontal_bullets"
        ordering = ["created"]


class MultiPageHorizontalTab(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    bullets = models.ManyToManyField(MultiPageHorizontalBullet)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_horizontal_tabs"
        ordering = ["created"]

class MultiPageTableData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    heading = models.CharField(max_length=255)
    data = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_table_data"
        ordering = ["created"]


class MultiPageTable(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    heading = models.CharField(max_length=255)
    datas = models.ManyToManyField(MultiPageTableData)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_table"
        ordering = ["created"]    


class MultiPageBulletPoints(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    bullet_point = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_bullet_points"
        ordering = ["created"]


class MultiPageTimeline(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    heading = models.CharField(max_length=255)
    summary = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_timelines"
        ordering = ["created"]


class TextEditor(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="course_text_editors")
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
        db_table = "course_text_editors"
        ordering = ["created"]


class MultiPageFaq(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, blank=True, null=True)

    question = models.CharField(max_length=255)
    answer = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipage_faqs"
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

    def __str__(self):
        return f"{self.title}-{self.company.name}"


class MultiPage(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="course_multipages")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="multipages")

    title = models.CharField(max_length = 255, blank=True, null=True)
    sub_title = models.CharField(max_length = 255, blank=True, null=True)

    summary = models.TextField(null=True, blank=True)
    description = RichTextField()

    meta_title = models.CharField(max_length=255)
    meta_tags = models.ManyToManyField(MetaTag)
    meta_description = models.TextField()

    url_type = models.CharField(max_length=50, default="slug_filtered")

    course_region = models.CharField(max_length=255, default="all")
    available_states = models.ManyToManyField(UniqueState, related_name="course_multipages")

    slider_courses = models.ManyToManyField(CourseDetail)

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
    bullet_points = models.ManyToManyField(MultiPageBulletPoints)    

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
        return f"{self.course.name}-{self.company.name}"
    
    class Meta:
        db_table = "course_multipages"
        ordering = ["created"]

    @property
    def get_rating(self):
        testimonials = self.course.course_testimonials.values_list("rating", flat=True)        
        
        return testimonials.aggregate(Avg('rating'))['rating__avg'] if testimonials else 0

    @property
    def slider_course_program_slug(self):
        if self.slider_courses.count() > 0:
            first_slider_course_detail = self.slider_courses.first()
            return first_slider_course_detail.course.program.slug
        
        return None
    
    @property
    def slider_course_specialization_slug(self):
        if self.slider_courses.count() > 0:
            first_slider_course_detail = self.slider_courses.first()
            return first_slider_course_detail.course.specialization.slug
        
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
    def get_available_states(self):
        if not self.available_states:
            return ""

        state_list = [state.name for state in self.available_states.all()]

        return ", ".join(state_list)
    
    @property
    def testimonials(self):
        return Testimonial.objects.filter(course = self.course, company = self.company)
    
    @property
    def blogs(self):
        from blog.models import Blog

        return Blog.objects.filter(course = self.course, company = self.company)
    
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

        toc += ["FAQs", "Tags", "Courses"]
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
    def image_count(self):
        if self.course.image:
            return 1
        
        return 0
        
