from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    options = models.JSONField()              # e.g. ["A", "B", "C", "D"]
    correct_index = models.PositiveIntegerField()
    explanation = models.TextField(blank=True)

    def __str__(self):
        return self.text[:50]