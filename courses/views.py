from django.shortcuts import get_object_or_404
from rest_framework import generics
from accounts.permissions import IsAdminOrReadOnly
from .models import Course, Question
from .serializers import (
    CourseSerializer, QuestionAdminSerializer, QuestionPublicSerializer,
)


class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Course.objects.all()
        if self.request.user.role != "admin":
            qs = qs.filter(is_published=True)   # students see published only
        return qs


class QuestionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.user.role == "admin":
            return QuestionAdminSerializer
        return QuestionPublicSerializer

    def get_queryset(self):
        return Question.objects.filter(course_id=self.kwargs["course_id"])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        serializer.save(course=course)