from rest_framework.pagination import LimitOffsetPagination

class ItemPagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50 

class MetaTagPagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50