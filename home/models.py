from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField


class HomeContent(models.Model):
    title = models.CharField(max_length=255, default="BZ India")
    description = RichTextField(default="BZ India is a joint venture group that partners with leading companies across diverse sectors to deliver top-tier services in the Indian market")    

    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()

    footer_text = RichTextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title[:25]}..." if len(self.title) > 25 else self.title
    
    class Meta:
        db_table = "home_main_content"


class State(models.Model):
    code = models.CharField(max_length=3, unique=True)    
    name = models.CharField(max_length=150, unique=True)

    slug = models.SlugField(null=True, blank=True, max_length=200)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            slug = base_slug
            count = 1

            while State.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "rel_states"
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(models.Model):
    code = models.CharField(max_length=3, unique=True)    
    name = models.CharField(max_length=150)

    state_code = models.CharField(max_length=5)
    state_name = models.CharField(max_length=150, blank=True, null=True)

    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts", null=True)

    slug = models.SlugField(null=True, blank=True, max_length=200)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            slug = base_slug
            count = 1

            while District.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "rel_districts"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.state.name}"
    

class SubDistrict(models.Model):
    code = models.CharField(max_length=10, unique=True, db_index = True)    
    name = models.CharField(max_length=150)

    district_code = models.CharField(max_length=10)
    district_name = models.CharField(max_length=150, blank=True, null=True)

    state_code = models.CharField(max_length=10)
    state_name = models.CharField(max_length=150, blank=True, null=True)

    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="sub_districts", null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="sub_districts", null=True)

    slug = models.SlugField(null=True, blank=True, max_length=200)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            slug = base_slug
            count = 1

            while SubDistrict.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "rel_sub_districts"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.district.name}, {self.state.name}"
    

class Village(models.Model):
    code = models.CharField(max_length=10, unique=True)    
    name = models.CharField(max_length=150, db_index=True)

    sub_district_code = models.CharField(max_length=10, db_index = True)
    sub_district_name = models.CharField(max_length=150, blank=True, null=True, db_index=True)

    district_code = models.CharField(max_length=10)
    district_name = models.CharField(max_length=150, blank=True, null=True, db_index=True)

    state_code = models.CharField(max_length=10)
    state_name = models.CharField(max_length=150, blank=True, null=True, db_index=True)

    sub_district = models.ForeignKey(SubDistrict, on_delete=models.CASCADE, related_name="villages", null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="villages", null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="villages", null=True)

    latitude = models.FloatField(blank=True, null=True, db_index=True)
    longitude = models.FloatField(blank=True, null=True, db_index=True)

    slug = models.SlugField(null=True, blank=True, max_length=200)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            slug = base_slug
            count = 1

            while Village.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "rel_villages"
        ordering = ["name"]

        indexes = [
            models.Index(fields=["name", "district_name", "state_name"]),
        ]

    def __str__(self):
        return f"{self.name}, {self.sub_district.name}, {self.district.name}, {self.state.name}"


class Pincode(models.Model):
    pincode = models.CharField(max_length=50)
    
    village_code = models.CharField(max_length=10, unique=True, db_index=True)    
    village_name = models.CharField(max_length=150)

    sub_district_code = models.CharField(max_length=10)
    sub_district_name = models.CharField(max_length=150, blank=True, null=True)

    district_code = models.CharField(max_length=10)
    district_name = models.CharField(max_length=150, blank=True, null=True)

    state_code = models.CharField(max_length=10)
    state_name = models.CharField(max_length=150, blank=True, null=True)

    slug = models.SlugField(null=True, blank=True, max_length=200)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.village_name}-{self.district_name}-{self.state_name}")

            slug = base_slug
            count = 1

            while Pincode.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "aaa_pincode"
        ordering = ["pincode"]

    def __str__(self):
        return f"{self.village_name}, {self.district_name}, {self.state_name}"
    

class Coordinates(models.Model):
    json_data = models.JSONField()
    
    village_code = models.CharField(max_length=10, unique=True)    
    village_name = models.CharField(max_length=150)

    sub_district_code = models.CharField(max_length=10)
    sub_district_name = models.CharField(max_length=150, blank=True, null=True)

    district_code = models.CharField(max_length=10)
    district_name = models.CharField(max_length=150, blank=True, null=True)

    state_code = models.CharField(max_length=10)
    state_name = models.CharField(max_length=150, blank=True, null=True)

    slug = models.SlugField(null=True, blank=True, max_length=200)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.village_name}-{self.district_name}-{self.state_name}")

            slug = base_slug
            count = 1

            while Pincode.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "rel_coordinates"
        ordering = ["village_name"]

    def __str__(self):
        return f"{self.village_name}, {self.district_name}, {self.state_name}"