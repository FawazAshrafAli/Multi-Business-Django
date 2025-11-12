from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BlogApiViewset, BlogArchivesViewSets

app_name = "blog_api"

router = DefaultRouter()

router.register(r'blogs', BlogApiViewset)
router.register(r'archives', BlogArchivesViewSets, basename="archives")

urlpatterns = [
    path('', include(router.urls)),
]
