from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q, Count
from .serializers import BlogSerializer
from blog.models import Blog
from django.db.models.functions import TruncMonth
from datetime import datetime
from utility.text import clean_string

from .paginations import BlogPagination

class BlogApiViewset(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    pagination_class = BlogPagination
    queryset = Blog.objects.none()
    lookup_field = "slug"

    def get_queryset(self):
        category = self.request.query_params.get("category")
        month_and_year = self.request.query_params.get("month_and_year")
        s = clean_string(self.request.query_params.get("s", ""))

        filters = Q(is_published = True)

        if (category or month_and_year or s):            

            if category:
                filters &= (Q(course__slug = category) | Q(product__slug = category) | Q(service__slug = category) | Q(registration_sub_type__slug = category))                

            if month_and_year:
                formated_month_and_year = datetime.strptime(month_and_year, "%Y-%m")
                filters &=  Q(
                    published_date__month = formated_month_and_year.month, 
                    published_date__year = formated_month_and_year.year
                    )
                
            if s:
                filters &= (
                        Q(title__icontains = s) | Q(course__name__icontains = s) | 
                        Q(product__name__icontains = s) | Q(service__name__icontains = s) |
                        Q(registration_sub_type__name__icontains = s) | Q(summary__icontains = s) |
                        Q(content__icontains = s)
                    )
        
        blogs = Blog.objects.filter(filters).select_related(
            "company"
        ).prefetch_related("meta_tags")

        return blogs      
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class BlogArchivesViewSets(viewsets.ViewSet):
    queryset = Blog.objects.none()

    def list(self, request, *args, **kwargs):        
        archive = (
            Blog.objects.filter(is_published=True)
            .annotate(month=TruncMonth("created"))
            .values("month")
            .annotate(published_month_count=Count("id"))
            .order_by("-month")
        )

        data = [
            {   
                "endpoint": entry["month"].strftime("%Y/%m"),
                "published_month_and_year": entry["month"].strftime("%B %Y"),
                "published_month_count": entry["published_month_count"],
            }
            for entry in archive
        ]

        return Response(data, status=status.HTTP_200_OK)