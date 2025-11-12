from django.db import models
from django.utils.text import slugify

class State(models.Model):
    name = models.CharField(max_length=150)    
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "states"
        ordering = ["name"]


class District(models.Model):
    name = models.CharField(max_length=150)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "districts"
        ordering = ["name"]


class Place(models.Model):
    name = models.CharField(max_length=150, db_index =True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, db_index =True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, db_index =True)
    pincode = models.PositiveIntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True, db_index =True)
    longitude = models.FloatField(blank=True, null=True, db_index =True)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Place.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "places"
        ordering = ["name"]


class TestedCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.latitude}-{self.longitude}"
    

class RetestedCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.latitude}-{self.longitude}"
    

class AndmanAndNicobarTestedCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.latitude}-{self.longitude}"
    

class TestPincode(models.Model):
    pincode = models.PositiveIntegerField()

    def __str__(self):
        return self.pincode


class UniqueState(models.Model):
    name = models.CharField(max_length=150, db_index=True)    
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while UniqueState.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "unique_states"
        ordering = ["name"]

    @property 
    def get_latitude(self):        
        qs = PlaceCoordinate.objects.filter(place__state=self).order_by("id")
        count = qs.count()
        if not count:
            return None

        # use offset to get middle record directly
        middle_obj = qs[count // 2]
        return middle_obj.latitude
    
    @property 
    def get_longitude(self):        
        qs = PlaceCoordinate.objects.filter(place__state=self).order_by("id")
        count = qs.count()
        if not count:
            return None

        # use offset to get middle record directly
        middle_obj = qs[count // 2]
        return middle_obj.longitude
    
    @property
    def get_pincode(self):
        pincode_obj = (
            PlacePincode.objects.filter(place__state=self)
            .order_by("id")
            .first()
        )
        if pincode_obj:
            return pincode_obj.pincode

        first_pincode_obj = (
            self.places.first().pincodes.first()
            if self.places.exists() else None
        )
        if first_pincode_obj:
            return first_pincode_obj.pincode

        return None

        


class UniqueDistrict(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name = "districts", db_index=True)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 2
            while UniqueDistrict.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "unique_districts"
        ordering = ["name"]

    @property
    def get_pincode(self):
        district_name = (self.name.replace("District", "")).strip()
        place = self.places.filter(
            name = district_name
            ).prefetch_related(
                "pincodes"
            ).first() or self.places.filter(
                name__icontains = district_name
            ).prefetch_related(
                "pincodes"
            ).first()
        
        if not place:
            place = self.places.prefetch_related(
                "pincodes"
            ).first()

        
        pincode_obj = place.pincodes.first()
        return pincode_obj.pincode
    
    @property
    def get_latitude(self):
        district_name = (self.name.replace("District", "")).strip()
        place = self.places.filter(
            name = district_name
            ).prefetch_related(
                "coordinates"
            ).first() or self.places.filter(
                name__icontains = district_name
            ).prefetch_related(
                "coordinates"
            ).first()
        
        if not place:
            place = self.places.prefetch_related(
                "coordinates"
            ).first()

        
        latitude_obj = place.coordinates.first()
        return latitude_obj.latitude
    
    @property
    def get_longitude(self):
        district_name = (self.name.replace("District", "")).strip()
        place = self.places.filter(
            name = district_name
            ).prefetch_related(
                "coordinates"
            ).first() or self.places.filter(
                name__icontains = district_name
            ).prefetch_related(
                "coordinates"
            ).first()
        
        if not place:
            place = self.places.prefetch_related(
                "coordinates"
            ).first()

        
        longitude_obj = place.coordinates.first()
        return longitude_obj.longitude


class PlaceCoordinate(models.Model):
    place = models.ForeignKey("UniquePlace", on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()


class PlacePincode(models.Model):
    place = models.ForeignKey("UniquePlace", on_delete=models.CASCADE)
    pincode = models.PositiveIntegerField(blank=True, null=True)


class UniquePlace(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    alt_name = models.CharField(max_length=150, blank=True, null=True)

    district = models.ForeignKey(UniqueDistrict, on_delete=models.CASCADE, related_name="places", db_index=True)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, related_name="places", db_index=True)

    pincodes = models.ManyToManyField(PlacePincode)

    coordinates = models.ManyToManyField(PlaceCoordinate)    
    
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug

            while UniquePlace.objects.filter(slug=slug).exists():
                place_district_slug = slugify(f"{base_slug}-{self.district.name}")

                if slug != place_district_slug:
                    slug = place_district_slug
                else:
                    slug = slugify(f"{base_slug}-{self.district.name}-{self.state.name}")
                    break

            self.slug = slug

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "unique_places"
        ordering = ["name"]

        indexes = [
            models.Index(fields=["name", "district", "state"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["district"]),
        ]

    @property
    def get_pincode(self):
        pincode_obj = self.pincodes.first()

        return pincode_obj.pincode if pincode_obj else None
    
    @property
    def get_latitude(self):
        coordinate = self.coordinates.first()

        return coordinate.latitude if coordinate else None
    
    @property
    def get_longitude(self):
        coordinate = self.coordinates.first()

        return coordinate.longitude if coordinate else None    


class UaeCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"UAE ({self.latitude}-{self.longitude})"
    

class KsaCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"KSA ({self.latitude}-{self.longitude})"
    

class KuwaitCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Kuwait ({self.latitude}-{self.longitude})"
    

class QatarCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Qatar ({self.latitude}-{self.longitude})"
    

class OmanCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Oman ({self.latitude}-{self.longitude})"
    

class IndiaCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"India ({self.latitude}-{self.longitude})"


class BahrainCoordinates(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Bahrain ({self.latitude}-{self.longitude})"
    

class UaeLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "uae_location_data"
        ordering = ["created"]


class KsaLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ksa_location_data"
        ordering = ["created"]

    
class KuwaitLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kuwait_location_data"
        ordering = ["created"]


class QatarLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "qatar_location_data"
        ordering = ["created"]


class OmanLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "oman_location_data"
        ordering = ["created"]


class IndiaLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    json_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "india_location_data"
        ordering = ["created"]


class BahrainLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_latitude = models.FloatField()
    requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bahrain_location_data"
        ordering = ["created"]


class PincodeAndCoordinate(models.Model):
    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE, related_name="pincode_and_coordinates")
    post_office_id = models.CharField(max_length=500)

    pincode = models.PositiveIntegerField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    slug = models.SlugField(max_length=500, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pincode} - {self.place.name} of {self.place.district.name}, {self.place.state.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.pincode}-{self.place.name}-{self.place.district.name}-{self.place.state.name}")

            slug = base_slug
            count = 1

            while PincodeAndCoordinate.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)


class IndiaLocationDataOld(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    place = models.OneToOneField(UniquePlace, on_delete=models.CASCADE)

    # requested_latitude = models.FloatField()
    # requested_longitude = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "india_location_data_old"
        ordering = ["created"]


# ##########################################################################
class IndianLocation(models.Model):
    source = models.OneToOneField(IndiaLocationData, on_delete=models.CASCADE)
    
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    state_code = models.CharField(max_length=10, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    suburb = models.CharField(max_length=100, blank=True, null=True)
    city_district = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    place_type = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    iso_codes = models.JSONField(blank=True, null=True)
    formatted = models.CharField(max_length=500, blank=True, null=True)
    confidence = models.IntegerField(blank=True, null=True)
    json_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)

    # --- Timestamps ---
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "indian_locations"
        indexes = [
            models.Index(fields=["state", "district"]),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["postcode"]),
        ]
        verbose_name = "Indian Location"
        verbose_name_plural = "Indian Locations"

    def __str__(self):
        return f"{self.suburb or self.town or self.village} ({self.state or ''})"


class SuburbLocationData(models.Model):
    json_data = models.JSONField()

    address = models.CharField(max_length=500)

    requested_place = models.CharField(max_length=150)
    json_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "suburb_location_data"
        ordering = ["created"]