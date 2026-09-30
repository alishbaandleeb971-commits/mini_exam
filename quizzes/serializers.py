from rest_framework import serializers
from .models import Attempt


class StartAttemptSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()


class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_index = serializers.IntegerField(min_value=0)


class AttemptSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Attempt
        fields = ["id", "course", "course_title", "status", "started_at", "finished_at", "score"]