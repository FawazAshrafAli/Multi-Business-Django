from django.db import models
from django.utils.text import slugify
import uuid

from locations.models import UniquePlace, UniqueDistrict, UniqueState
from registration.models import RegistrationSubType

class PostOffice(models.Model):
    circle_name = models.CharField(max_length=150, null=True, blank=True)
    region_name = models.CharField(max_length=150, null=True, blank=True)
    division_name = models.CharField(max_length=150, null=True, blank=True)
    office_name = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.PositiveIntegerField(null=True, blank=True)
    office_type = models.CharField(max_length=150, null=True, blank=True)
    delivery = models.BooleanField(default=False, null=True, blank=True)
    district = models.CharField(max_length=150, null=True, blank=True)
    state_name = models.CharField(max_length=150, null=True, blank=True)
    latitude = models.CharField(max_length=150, null=True, blank=True)
    longitude = models.CharField(max_length=150, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pincode}"
    
    class Meta:
        db_table = "post_offices"
        ordering = ["pincode"]


class PoliceStation(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    name_gujarati = models.CharField(max_length=250, null=True, blank=True)
    name_goan_konkani = models.CharField(max_length=250, null=True, blank=True)
    name_santali = models.CharField(max_length=250, null=True, blank=True)
    name_hindi = models.CharField(max_length=250, null=True, blank=True)
    name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    name_punjabi = models.CharField(max_length=250, null=True, blank=True) #name:pnb
    name_telugu = models.CharField(max_length=250, null=True, blank=True)
    name_kannada = models.CharField(max_length=250, null=True, blank=True)
    name_bengali = models.CharField(max_length=250, null=True, blank=True)
    name_marathi = models.CharField(max_length=250, null=True, blank=True)
    name_tamil = models.CharField(max_length=250, null=True, blank=True)
    name_odiya = models.CharField(max_length=250, null=True, blank=True)
    name_assamese = models.CharField(max_length=250, null=True, blank=True)
    name_kashmiri = models.CharField(max_length=250, null=True, blank=True)
    name_urdu = models.CharField(max_length=250, null=True, blank=True)
    name_maithili = models.CharField(max_length=250, null=True, blank=True)
    name_sanskrit = models.CharField(max_length=250, null=True, blank=True)

    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)    
    phone = models.CharField(max_length=120, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name or f"Police Station {self.osm_id}"

    class Meta:
        verbose_name = "Police Station"
        verbose_name_plural = "Police Stations"
        db_table = "police_stations"


class Bank(models.Model):
    name = models.CharField(max_length=150)
    ifsc = models.CharField(max_length=20)
    branch = models.CharField(max_length=150)
    center = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    address = models.TextField()
    contact = models.CharField(max_length=50)
    
    iso3166 = models.CharField(max_length=50)
    micr = models.CharField(max_length=50)
    swift = models.CharField(max_length=50, blank=True, null=True)

    imps = models.BooleanField(default=False)
    rtgs = models.BooleanField(default=False)
    neft = models.BooleanField(default=False)
    upi = models.BooleanField(default=False)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:   
            base_slug = slugify(f"{self.name}-{self.ifsc}")
            slug = base_slug
            count = 1
            while Bank.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1
            
            self.slug = slug

        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Bank"
        verbose_name_plural = "Banks"
        
        db_table = "banks"
        ordering = ["ifsc"]

    def __str__(self):
        return f"{self.name}-{self.branch}"


class TouristAttraction(models.Model):
    image = models.ImageField(upload_to="attractions/", null=True, blank=True)

    name = models.CharField(max_length=250, null=True, blank=True)
    old_name = models.CharField(max_length=250, null=True, blank=True)
    alternative_name = models.CharField(max_length=250, null=True, blank=True) #alt_name:en        
    short_name = models.CharField(max_length=150, null=True, blank=True)

    # Name in different language
    alternative_name_hindi = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_bengali = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_marathi = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_kannada = models.CharField(max_length=250, null=True, blank=True) #alt_name:kn
    alternative_name_maithili = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_tamil = models.CharField(max_length=250, null=True, blank=True)

    name_gujarati = models.CharField(max_length=250, null=True, blank=True)
    name_goan_konkani = models.CharField(max_length=250, null=True, blank=True)
    name_santali = models.CharField(max_length=250, null=True, blank=True)
    name_hindi = models.CharField(max_length=250, null=True, blank=True)
    name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    name_punjabi = models.CharField(max_length=250, null=True, blank=True) #name:pnb
    name_telugu = models.CharField(max_length=250, null=True, blank=True)
    name_kannada = models.CharField(max_length=250, null=True, blank=True)
    name_bengali = models.CharField(max_length=250, null=True, blank=True)
    name_marathi = models.CharField(max_length=250, null=True, blank=True)
    name_tamil = models.CharField(max_length=250, null=True, blank=True)
    name_odiya = models.CharField(max_length=250, null=True, blank=True)
    name_assamese = models.CharField(max_length=250, null=True, blank=True)
    name_kashmiri = models.CharField(max_length=250, null=True, blank=True)
    name_urdu = models.CharField(max_length=250, null=True, blank=True)
    name_maithili = models.CharField(max_length=250, null=True, blank=True)
    name_sanskrit = models.CharField(max_length=250, null=True, blank=True)

    historic_type = models.CharField(max_length=150, null=True, blank=True)

    # accessibility
    wheelchair_accessible = models.CharField(max_length=50, null=True, blank=True)

    # sports availability
    sport_type = models.CharField(max_length=50, null=True, blank=True)

    # Leisure Activity
    leisure_activity = models.CharField(max_length=50, null=True, blank=True)

    # Religious
    denomination = models.CharField(max_length=50, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)

    # Geography
    house_number = models.CharField(max_length=150, null=True, blank=True) #addr:housenumber # addr:housename
    pincode = models.CharField(max_length=250, null=True, blank=True) #postcode #addr:postcode
    street = models.CharField(max_length=350, null=True, blank=True) #addr:street
    place = models.CharField(max_length=150, null=True, blank=True) #addr:place
    city = models.CharField(max_length=150, null=True, blank=True) #addr:city 
    district = models.CharField(max_length=150, null=True, blank=True) #addr:district 
    state = models.CharField(max_length=150, null=True, blank=True) #addr:state 
    place_type = models.CharField(max_length=250, null=True, blank=True) #place
    building_type = models.CharField(max_length=150, null=True, blank=True) #amenity
    building_category = models.CharField(max_length=150, null=True, blank=True) #building
    elevation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #ele
    geography_type = models.CharField(max_length=150, null=True, blank=True) #natural
    man_made_contribution = models.CharField(max_length=150, null=True, blank=True) #man_made
    memmorial_type = models.CharField(max_length=50, null=True, blank=True) #memorial

    building_height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #height

    waterway_type = models.CharField(max_length=150, null=True, blank=True) #waterway 
    waterbody_type = models.CharField(max_length=150, null=True, blank=True) #water
    castle_type = models.CharField(max_length=150, null=True, blank=True) #castle
    attraction = models.CharField(max_length=150, null=True, blank=True)

    # operation data
    operated_by = models.CharField(max_length=250, null=True, blank=True)
    opening_hours = models.CharField(max_length=150, null=True, blank=True)
    access_type = models.CharField(max_length=150, null=True, blank=True) #access

    started_date = models.CharField(max_length=150, null=True, blank=True) #start_date

    # shopping
    shops_available = models.CharField(max_length=150, null=True, blank=True) #shop

    # description
    description = models.TextField(null=True, blank=True)
    note = models.CharField(max_length=150, null=True, blank=True)

    # contact
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    #website
    website = models.URLField(max_length=200, null=True, blank=True)    

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    class Meta:
        db_table = "attractions"
        ordering = ["created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.name:
                base_slug = slugify(self.name)

                slug = base_slug
                count = 1

                while TouristAttraction.objects.filter(slug = slug).exists():
                    slug = f"{base_slug}{count}"
                    count += 1

                self.slug = slug

            else:
                self.slug = uuid.uuid4()
        
        if not self.name:
            names = [
                self.name, self.old_name, self.alternative_name,

                self.name_gujarati, self.name_goan_konkani, self.name_santali, self.name_hindi, 
                self.name_malayalam, self.name_punjabi, self.name_telugu, self.name_kannada, 
                self.name_bengali, self.name_marathi, self.name_tamil, self.name_odiya, 
                self.name_assamese, self.name_kashmiri, self.name_urdu, self.name_maithili, 
                self.name_sanskrit, 

                self.alternative_name_hindi, self.alternative_name_bengali, 
                self.alternative_name_marathi, self.alternative_name_kannada,
                self.alternative_name_maithili, self.alternative_name_malayalam,
                self.alternative_name_tamil,

                self.short_name
            ]

            available_names = [name for name in names if name]

            if available_names:
                self.name = available_names[0]

        super().save(*args, **kwargs)


    @property
    def attraction_type(self):        
        if self.historic_type and self.historic_type!= "yes":
            return str(self.historic_type).title()
        elif self.waterway_type and self.waterway_type!= "yes":
            return str(self.waterway_type).title()
        elif self.waterbody_type and self.waterbody_type!= "yes":
            return str(self.waterbody_type).title()
        return None
    
    @property
    def get_place(self):
        return self.place or self.city or None
    
    @property
    def get_absolute_url(self):
        return f'https://bzindia/destinations/{self.slug}'
    

class Destination(models.Model):
    image = models.ImageField(upload_to="destinations/", null=True, blank=True)

    name = models.CharField(max_length=250, null=True, blank=True)
    old_name = models.CharField(max_length=250, null=True, blank=True)
    alternative_name = models.CharField(max_length=250, null=True, blank=True) #alt_name:en        
    short_name = models.CharField(max_length=150, null=True, blank=True)

    # Name in different language
    alternative_name_hindi = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_bengali = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_marathi = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_kannada = models.CharField(max_length=250, null=True, blank=True) #alt_name:kn
    alternative_name_maithili = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    alternative_name_tamil = models.CharField(max_length=250, null=True, blank=True)

    name_gujarati = models.CharField(max_length=250, null=True, blank=True)
    name_goan_konkani = models.CharField(max_length=250, null=True, blank=True)
    name_santali = models.CharField(max_length=250, null=True, blank=True)
    name_hindi = models.CharField(max_length=250, null=True, blank=True)
    name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    name_punjabi = models.CharField(max_length=250, null=True, blank=True) #name:pnb
    name_telugu = models.CharField(max_length=250, null=True, blank=True)
    name_kannada = models.CharField(max_length=250, null=True, blank=True)
    name_bengali = models.CharField(max_length=250, null=True, blank=True)
    name_marathi = models.CharField(max_length=250, null=True, blank=True)
    name_tamil = models.CharField(max_length=250, null=True, blank=True)
    name_odiya = models.CharField(max_length=250, null=True, blank=True)
    name_assamese = models.CharField(max_length=250, null=True, blank=True)
    name_kashmiri = models.CharField(max_length=250, null=True, blank=True)
    name_urdu = models.CharField(max_length=250, null=True, blank=True)
    name_maithili = models.CharField(max_length=250, null=True, blank=True)
    name_sanskrit = models.CharField(max_length=250, null=True, blank=True)

    historic_type = models.CharField(max_length=150, null=True, blank=True)

    # accessibility
    wheelchair_accessible = models.CharField(max_length=50, null=True, blank=True)

    # sports availability
    sport_type = models.CharField(max_length=50, null=True, blank=True)

    # Leisure Activity
    leisure_activity = models.CharField(max_length=50, null=True, blank=True)

    # Religious
    denomination = models.CharField(max_length=50, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)

    # Geography
    house_number = models.CharField(max_length=150, null=True, blank=True) #addr:housenumber # addr:housename
    pincode = models.CharField(max_length=250, null=True, blank=True) #postcode #addr:postcode
    street = models.CharField(max_length=350, null=True, blank=True) #addr:street
    place = models.CharField(max_length=150, null=True, blank=True) #addr:place
    city = models.CharField(max_length=150, null=True, blank=True) #addr:city 
    district = models.CharField(max_length=150, null=True, blank=True) #addr:district 
    state = models.CharField(max_length=150, null=True, blank=True) #addr:state 
    place_type = models.CharField(max_length=250, null=True, blank=True) #place
    building_type = models.CharField(max_length=150, null=True, blank=True) #amenity
    building_category = models.CharField(max_length=150, null=True, blank=True) #building
    elevation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #ele
    geography_type = models.CharField(max_length=150, null=True, blank=True) #natural
    man_made_contribution = models.CharField(max_length=150, null=True, blank=True) #man_made
    memmorial_type = models.CharField(max_length=50, null=True, blank=True) #memorial

    building_height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #height

    waterway_type = models.CharField(max_length=150, null=True, blank=True) #waterway 
    waterbody_type = models.CharField(max_length=150, null=True, blank=True) #water
    castle_type = models.CharField(max_length=150, null=True, blank=True) #castle
    attraction = models.CharField(max_length=150, null=True, blank=True)

    # operation data
    operated_by = models.CharField(max_length=250, null=True, blank=True)
    opening_hours = models.CharField(max_length=150, null=True, blank=True)
    access_type = models.CharField(max_length=150, null=True, blank=True) #access

    started_date = models.CharField(max_length=150, null=True, blank=True) #start_date

    # shopping
    shops_available = models.CharField(max_length=150, null=True, blank=True) #shop

    # description
    description = models.TextField(null=True, blank=True)
    note = models.CharField(max_length=150, null=True, blank=True)

    # contact
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    #website
    website = models.URLField(max_length=200, null=True, blank=True)    

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    class Meta:
        db_table = "destinations"
        ordering = ["created"]

    def save(self, *args, **kwargs):
        base_name = self.name
        if not self.name:
            names = [
                self.name, self.old_name, self.alternative_name,

                self.name_gujarati, self.name_goan_konkani, self.name_santali, self.name_hindi, 
                self.name_malayalam, self.name_punjabi, self.name_telugu, self.name_kannada, 
                self.name_bengali, self.name_marathi, self.name_tamil, self.name_odiya, 
                self.name_assamese, self.name_kashmiri, self.name_urdu, self.name_maithili, 
                self.name_sanskrit, 

                self.alternative_name_hindi, self.alternative_name_bengali, 
                self.alternative_name_marathi, self.alternative_name_kannada,
                self.alternative_name_maithili, self.alternative_name_malayalam,
                self.alternative_name_tamil,

                self.short_name
            ]

            available_names = [name for name in names if name]

            if available_names:
                self.name = available_names[0]
                base_name = self.name

        if not self.slug:
            if base_name and slugify(base_name) != "":
                base_slug = slugify(base_name)

                slug = base_slug
                count = 1

                while Destination.objects.filter(slug = slug).exists():
                    slug = f"{base_slug}{count}"
                    count += 1

                self.slug = slug

            else:
                self.slug = uuid.uuid4()        

        super().save(*args, **kwargs)


    @property
    def attraction_type(self):        
        if self.historic_type and self.historic_type!= "yes":
            return str(self.historic_type).title()
        elif self.waterway_type and self.waterway_type!= "yes":
            return str(self.waterway_type).title()
        elif self.waterbody_type and self.waterbody_type!= "yes":
            return str(self.waterbody_type).title()
        return None
    
    @property
    def get_place(self):
        return self.place or self.city or None
    
    @property
    def get_absolute_url(self):
        return f'https://bzindia/destinations/{self.slug}'


class Court(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)

    old_name = models.CharField(max_length=250, blank=True, null=True)

    name_gujarati = models.CharField(max_length=250, null=True, blank=True)
    name_goan_konkani = models.CharField(max_length=250, null=True, blank=True)
    name_santali = models.CharField(max_length=250, null=True, blank=True)
    name_hindi = models.CharField(max_length=250, null=True, blank=True)
    name_malayalam = models.CharField(max_length=250, null=True, blank=True)
    name_punjabi = models.CharField(max_length=250, null=True, blank=True) #name:pnb
    name_telugu = models.CharField(max_length=250, null=True, blank=True)
    name_kannada = models.CharField(max_length=250, null=True, blank=True)
    name_bengali = models.CharField(max_length=250, null=True, blank=True)
    name_marathi = models.CharField(max_length=250, null=True, blank=True)
    name_tamil = models.CharField(max_length=250, null=True, blank=True)
    name_odiya = models.CharField(max_length=250, null=True, blank=True)
    name_assamese = models.CharField(max_length=250, null=True, blank=True)
    name_kashmiri = models.CharField(max_length=250, null=True, blank=True)
    name_urdu = models.CharField(max_length=250, null=True, blank=True)
    name_maithili = models.CharField(max_length=250, null=True, blank=True)
    name_sanskrit = models.CharField(max_length=250, null=True, blank=True)

    designation = models.CharField(max_length=250, null=True, blank=True)

    street = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=250, blank=True, null=True)
    district = models.CharField(max_length=250, blank=True, null=True)
    state = models.CharField(max_length=250, blank=True, null=True)
    pincode = models.PositiveIntegerField(null=True, blank=True)
    
    phone = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)

    opening_hours = models.CharField(max_length=250, blank=True, null=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    class Meta:
        db_table="courts"


class CscCenter(models.Model):
    csc_id = models.CharField(max_length = 50, null=True, blank=True)

    title = models.CharField(max_length=500, null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    slug = models.SlugField(blank=True, null=True, max_length=500, db_index=True)
    
    state_name = models.CharField(max_length=150, blank=True, null=True)
    state = models.ForeignKey(UniqueState, on_delete=models.CASCADE, blank=True, null=True)

    district_name = models.CharField(max_length=150, blank=True, null=True)
    district = models.ForeignKey(UniqueDistrict, on_delete=models.CASCADE, blank=True, null=True)

    place_name = models.CharField(max_length=150, blank=True, null=True)
    place = models.ForeignKey(UniquePlace, on_delete=models.CASCADE, blank=True, null=True)

    location = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=15, blank=True, null=True)
    street = models.CharField(max_length=500, null=True, blank=True)
    
    logo = models.ImageField(upload_to='csc_center_logos/', blank=True, null=True)

    description = models.TextField(null=True, blank=True)
    owner = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    website = models.URLField(max_length=100, null=True, blank=True)

    contact_number = models.CharField(max_length=25, null=True, blank=True)
    mobile_number = models.CharField(max_length=25, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=25, null=True, blank=True)

    all_registrations = models.TextField(null=True, blank=True)

    latitude = models.CharField(max_length=20, null=True)
    longitude = models.CharField(max_length=20, null=True)

    decimal_latitude = models.FloatField(blank=True, null=True, db_index =True)
    decimal_longitude = models.FloatField(blank=True, null=True, db_index =True)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if len(self.latitude) > 10:
            self.latitude = None

        if len(self.longitude) > 10:
            self.longitude = None

        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.place.name}-{self.district.name}-{self.state.name}")

            slug = base_slug
            count = 2
            while CscCenter.objects.filter(slug = slug).exists():
                slug = f"{base_slug}{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "csc_centers"
        ordering = ["name"]
        verbose_name = "CSC"
        verbose_name_plural = "CSCs"    