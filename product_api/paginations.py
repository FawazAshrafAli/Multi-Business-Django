from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

class ProductDetailPagination(PageNumberPagination):
    page_size = 9

class ProductMultipagePagination(PageNumberPagination):
    page_size = 9

class OrderPagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50