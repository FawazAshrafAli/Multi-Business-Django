from django.urls import path

from .views import (
    GetSpecializationsView, GetCourseView, GetProgramsView,
    HomeView, CourseDetailView, GetCourseDetailsView
    )

app_name = "education"

urlpatterns = [
    path('<str:slug>', HomeView.as_view(), name="home"),

    path('get_specializations/', GetSpecializationsView.as_view(), name="get_specializations"),
    path('get_courses/', GetCourseView.as_view(), name="get_courses"),
    path('get_course_details/', GetCourseDetailsView.as_view(), name="get_course_details"),
    path('get_programs/', GetProgramsView.as_view(), name="get_programs"),

    path('<str:slug>/', CourseDetailView.as_view(), name="course"),
]
