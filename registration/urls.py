from django.urls import path

from .views import (
    GetRegistrationSubTypeView, GetRegistrationTypeView, 
    GetRegistrationDetailView, GetRegistrationsView
    )

app_name = "registration"

urlpatterns = [
    path('get_registration_sub_types/', GetRegistrationSubTypeView.as_view(), name="get_registration_sub_types"),
    path('get_types/', GetRegistrationTypeView.as_view(), name="get_types"),
    path('get_registration_details/', GetRegistrationDetailView.as_view(), name="get_registration_details"),
    path('get_registrations/', GetRegistrationsView.as_view(), name="get_registrations"),
]
