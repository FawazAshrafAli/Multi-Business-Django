from django.db import models
from django.utils.text import slugify

from locations.models import UniqueState

class Enquiry(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    company_sub_type = models.CharField(max_length=250, blank=True, null=True)
    item = models.CharField(max_length=250, blank=True, null=True)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="enquiries")
    comment = models.TextField()

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.email}")

            slug = base_slug
            count = 1

            while Enquiry.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "enquiry"
        ordering = ["created"]

    def __str__(self):
        return self.email
