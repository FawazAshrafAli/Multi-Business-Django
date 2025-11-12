from django.urls import path
from .views import sitemap_urls, product_sitemap_urls, product_sitemap_count

app_name="sitemap"

urlpatterns = [
    path("", sitemap_urls, name="sitemap"),
    path("products/", product_sitemap_urls, name="products"),
    path("product_count/", product_sitemap_count, name="product_count"),
]
