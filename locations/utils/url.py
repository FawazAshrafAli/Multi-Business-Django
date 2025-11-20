from locations.models import UniquePlace, UniqueDistrict, UniqueState

def generate_location_url_tails(state_ids = None):
    state_filters = {}
    district_filters = {}
    place_filters = {}

    if state_ids:
        state_filters["id__in"] = state_ids
        district_filters["state__id__in"] = state_ids
        place_filters["state__id__in"] = state_ids

    for slug in UniqueState.objects.filter(**state_filters).values_list("slug", flat=True).iterator():
        yield f"/{slug}"

    for state, slug in UniqueDistrict.objects.filter(**district_filters).values_list("state__slug", "slug").iterator():
        yield f"/{state}/{slug}"

    for state, district, slug in UniquePlace.objects.filter(**place_filters).values_list(
        "state__slug", "district__slug", "slug"
    ).iterator():
        yield f"/{state}/{district}/{slug}"

def generate_location_url_slugs(state_ids = None):
    state_filters = {}
    district_filters = {}
    place_filters = {}

    if state_ids:
        state_filters["id__in"] = state_ids
        district_filters["state__id__in"] = state_ids
        place_filters["state__id__in"] = state_ids

    seen = set()
    for model, filters in [
        (UniqueState, state_filters),
        (UniqueDistrict, district_filters),
        (UniquePlace, place_filters),
    ]:
        for slug in model.objects.filter(**filters).values_list("slug", flat=True).iterator():
            if slug and slug not in seen:
                seen.add(slug)

    for slug in sorted(seen):
        yield slug


def generate_state_slugs():
    states = UniqueState.objects.all()    

    slugs = states.values_list("slug", flat=True).distinct()

    for slug in slugs.order_by("slug").iterator():
        if slug:
            yield slug


def generate_district_slugs():
    districts = UniqueDistrict.objects.all()    

    slugs = districts.values_list("slug", flat=True).distinct()

    for slug in slugs.order_by("slug").iterator():
        if slug:
            yield slug


def generate_district_dicts():
    district_dicts = UniqueDistrict.objects.values("slug", "state__slug", "name", "state__name")

    for item in district_dicts.iterator():
        yield {"slug": item["slug"], "state_slug": item["state__slug"], "name": item["name"], "state_name": item["state__name"]}


def generate_place_dicts():
    place_dicts = UniquePlace.objects.values("slug", "district__slug")

    for item in place_dicts.iterator():
        yield {"slug": item["slug"], "district_slug": item["district__slug"]}

def generate_state_dicts():
    state_dicts = UniqueState.objects.values("slug", "name")

    for item in state_dicts.iterator():
        yield {"slug": item["slug"], "name": item["name"]}
