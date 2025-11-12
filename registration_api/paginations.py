from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination   

class RegistrationPagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50 

class RegistrationMultipagePagination(PageNumberPagination):
    page_size = 3