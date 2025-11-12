from rest_framework.pagination import PageNumberPagination

class BlogPagination(PageNumberPagination):
    page_size = 15

class CategoryItemsPagination(PageNumberPagination):
    page_size = 1