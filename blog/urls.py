from django.urls import path
from .feeds import BlogFeed, BlogDetailFeed

app_name = "blog"

urlpatterns = [
    path("feed/", BlogFeed()),
    path("<str:blog_slug>/feed", BlogDetailFeed()),
]
