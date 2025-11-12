from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MetaTagApiViewset, ItemViewSet, MostMatchingCompanyViewSet

app_name = "meta_tag_api"

router = DefaultRouter()

router.register(r'tags', MetaTagApiViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('matching_items/<str:slug>/', ItemViewSet.as_view({"get": "list"})),
    path('most-matching-company/<str:slug>/', MostMatchingCompanyViewSet.as_view({"get": "list"})),
]
