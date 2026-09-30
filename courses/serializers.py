from rest_framework import serializers
from .models import Course, Question


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "is_published"]


class QuestionAdminSerializer(serializers.ModelSerializer):
    """Full view, used by admins. Includes the answer."""

    class Meta:
        model = Question
        fields = ["id", "text", "options", "correct_index", "explanation"]

    def validate(self, data):
        options = data.get("options", [])
        if not isinstance(options, list) or len(options) < 2:
            raise serializers.ValidationError("options must be a list of at least 2 items.")
        if data["correct_index"] >= len(options):
            raise serializers.ValidationError("correct_index is out of range.")
        return data


class QuestionPublicSerializer(serializers.ModelSerializer):
    """Student view. No correct_index, no explanation."""

    class Meta:
        model = Question
        fields = ["id", "text", "options"]