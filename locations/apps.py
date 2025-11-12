from django.apps import AppConfig


class LocationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'locations'

    # def ready(self):
    #     from .trie_loader import load_location_data
    #     load_location_data()