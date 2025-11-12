from rest_framework.pagination import PageNumberPagination

class ProductDetailPagination(PageNumberPagination):
    page_size = 9

class ProductMultipagePagination(PageNumberPagination):
    page_size = 9