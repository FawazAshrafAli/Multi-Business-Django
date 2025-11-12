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