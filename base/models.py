from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

class MetaTag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = RichTextField(null=True, blank=True)

    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.name} - BZ India"

        if not self.slug:
            base_slug = slugify(self.name)

            slug = base_slug
            count = 1

            while MetaTag.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"

                count += 1

            self.slug = slug     

        super().save(*args, **kwargs)

    class Meta:
        db_table = "meta_tags"
        ordering = ["name"]