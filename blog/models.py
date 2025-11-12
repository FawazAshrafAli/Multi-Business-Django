from django.db import models
from django.db.models import Q
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField

from company.models import Company
from base.models import MetaTag

class Blog(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="blogs/", null=True, blank=True)

    blog_type = models.CharField(max_length=150)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name="blogs")

    summary = models.TextField()
    content = RichTextField()
    meta_description = models.TextField()
    
    meta_tags = models.ManyToManyField(MetaTag)

    is_published = models.BooleanField(default=False)

    published_date = models.DateTimeField(blank=True, null=True)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if self.is_published:
            self.published_date = timezone.now()
        else:
            self.published_date = None

        if not self.slug:            
            base_slug = slugify({self.title})

            slug = base_slug
            count = 1

            while Blog.objects.filter(slug = slug).exclude(pk = self.pk).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "blogs"
        ordering = ["-created"]
    
    @property
    def get_image_name(self):
        if self.image:
            return self.image.name.replace("blogs/", "")
        
        return None
        
    @property
    def get_meta_tags(self):
        if not self.meta_tags.exists():
            return ""

        tag_list = [tag.name for tag in self.meta_tags.all()]

        return ", ".join(tag_list)
    
    @property
    def get_absolute_url(self):
        return f"https://bzindia/learn/{self.slug}"    
    
    @property
    def get_published_on(self):
        from datetime import datetime

        if self.published_date:            
            return datetime.strftime(self.published_date, "%b %d, %Y")
        
        return None
    