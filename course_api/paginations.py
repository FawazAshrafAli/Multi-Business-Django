from rest_framework.pagination import LimitOffsetPagination

class CoursePagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50 

class CourseMultipagePagination(LimitOffsetPagination):
    default_limit = 9
    max_limit = 50