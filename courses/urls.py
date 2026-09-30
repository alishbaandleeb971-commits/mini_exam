from django.urls import path
from .views import CourseListCreateView, QuestionListCreateView

urlpatterns = [
    path("", CourseListCreateView.as_view()),
    path("<int:course_id>/questions/", QuestionListCreateView.as_view()),
]