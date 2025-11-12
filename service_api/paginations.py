from rest_framework.pagination import LimitOffsetPagination

class ServiceDetailPagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50 

class ServiceMultipagePagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50 