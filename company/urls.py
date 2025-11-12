from django.urls import path

from .views import get_company, GetFilteredCompaniesView

app_name = "company"

urlpatterns = [
    # path("<str:slug>", CompanyHomePageView.as_view(), name="company_home"),
    path("get_company/<str:slug>", get_company, name="get_company"),
    path("get_filtered_companies/", GetFilteredCompaniesView.as_view(), name="get_filtered_companies"),
]
