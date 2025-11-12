import pandas as pd
import logging
from .views import row_generator
import time
from django.db import transaction
from celery import shared_task

logger = logging.getLogger(__name__)

def clean_string(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value if value and value.lower() != "nan" else None

def clean_number(value):
    try:
        if not value or pd.isna(value):
            return None
        number = str(value).split(',')[0].replace("+91", "").replace("'", "").strip()
        return int(float(number))
    except Exception:
        return None

@shared_task(queue="worker4_queue")
def import_csc_centers():
    from .models import CscCenter
    from locations.models import UniquePlace, UniqueDistrict, UniqueState    
    from registration.models import RegistrationSubType, RegistrationType
    from company.models import Company
    from django.utils.text import slugify

    csv_data = pd.read_csv(r'D:\Projects\CSC\csc\static\w3\admin_csc_center\documents\csc-centers.csv')
    length = len(csv_data)

    company = Company.objects.filter(type__name="Registration").first()
    if not company:
        return "Failed! Registration company not found."

    registration_type, _ = RegistrationType.objects.get_or_create(company=company, name="Service")

    logger.info("Importing data . . .")

    for index, row in row_generator(csv_data):
        try:
            time.sleep(0.001)

            state_name = clean_string(row.get("cs_state"))
            district_name = clean_string(row.get("cs_district"))
            place_name = clean_string(row.get("cs_block"))

            state = None
            district = None
            place = None

            try:
                state = UniqueState.objects.get(name=state_name)
            except UniqueState.DoesNotExist:
                pass
                
            try:
                district = UniqueDistrict.objects.get(name=district_name, state__name=state)
            except UniqueDistrict.DoesNotExist:
                pass

            try:
                place= UniquePlace.objects.get(name=place_name, state__name=state, district__name=district)
            except UniquePlace.DoesNotExist:
                pass

            csc_id = f"CSC{row['ID']}"
            if not CscCenter.objects.filter(csc_id=csc_id).exists():
                with transaction.atomic():
                    contact_number = clean_number(row.get("csc_phone"))
                    mobile_number = clean_number(row.get("csc_phonetwo"))

                    if not contact_number and mobile_number:
                        contact_number = mobile_number

                    csc_center = CscCenter.objects.create(
                        csc_id=csc_id,
                        name=clean_string(row.get("csc_name")),
                        slug=slugify(clean_string(row.get("Slug"))),
                        state=state,
                        district=district,
                        place=place,
                        location=clean_string(row.get("cs_address")),
                        pincode=clean_string(row.get("csc_pincode")),
                        street=clean_string(row.get("csc_place")),
                        owner=clean_string(row.get("CSC Owner Name")),
                        email = clean_string(row.get("csc_email") or row.get("CSC Email")),
                        contact_number=contact_number,
                        mobile_number=mobile_number,
                        latitude=clean_string(row.get("csc_latitude")),
                        longitude=clean_string(row.get("csc_longitude")),
                    )

                    whatsapp = clean_string(row.get("csc_whatsapp"))
                    if whatsapp:
                        parts = whatsapp.split(",")
                        csc_center.whatsapp_number = parts[0].strip()
                        if len(parts) > 1 and not csc_center.mobile_number:
                            csc_center.mobile_number = clean_number(parts[1])

                    services = row.get("Services")
                    if services and isinstance(services, str):
                        for registration in services.split(","):
                            reg_name = registration.strip()
                            reg_obj, _ = RegistrationSubType.objects.get_or_create(
                                name=reg_name, type=registration_type, company=company
                            )
                            csc_center.registrations.add(reg_obj)

                    csc_center.save()

            logger.info(f"Processed row {index + 1} of {length}")

        except Exception as e:
            logger.error(f"Error processing row {index + 1}: {e} | Row: {row.to_dict()}")
            continue

    logger.info("Importing Completed!")
