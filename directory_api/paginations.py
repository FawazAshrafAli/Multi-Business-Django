from rest_framework.pagination import LimitOffsetPagination
from directory.models import CscCenter

class CscPagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50
    