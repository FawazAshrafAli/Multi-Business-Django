from rest_framework.pagination import LimitOffsetPagination

class BlogPagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50 