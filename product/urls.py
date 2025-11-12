from django.urls import path
from .views import HomeView, GetSubCategoriesView, GetProductsView, GetCategoriesView

app_name = "product"

urlpatterns = [
    path('<str:slug>', HomeView.as_view(), name="home"),

    path('get_sub_categories/', GetSubCategoriesView.as_view(), name = "get_sub_categories"),
    path('get_categories/', GetCategoriesView.as_view(), name = "get_categories"),
    path('get_products/', GetProductsView.as_view(), name = "get_products"),
]
