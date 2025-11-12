from django.urls import path
from .views import GetPincodeView, GetLocalPlacesView

app_name = "base"

urlpatterns = [
    path('<str:latitude>/<str:longitude>/', GetPincodeView.as_view(), name="get_pincode"),
    path('get_places/<pincode>', GetLocalPlacesView.as_view(), name="get_places"),
]
