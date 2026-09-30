from django.conf import settings
from django.db import models
from django.db.models import Q
from courses.models import Course, Question


class Attempt(models.Model):
    STATUS_CHOICES = [("in_progress", "In progress"), ("finished", "Finished")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attempts")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="in_progress")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            # the database itself allows only one in-progress attempt per user per course
            models.UniqueConstraint(
                fields=["user", "course"],
                condition=Q(status="in_progress"),
                name="one_in_progress_per_course",
            )
        ]


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_index = models.PositiveIntegerField()
    is_correct = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="one_answer_per_question")
        ]