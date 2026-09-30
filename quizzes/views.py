from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Question
from .models import Attempt, Answer
from .serializers import StartAttemptSerializer, AnswerInputSerializer, AttemptSerializer


def get_attempt_for(request, pk, owner_only=False):
    attempt = get_object_or_404(Attempt.objects.select_related("course"), pk=pk)
    is_owner = attempt.user_id == request.user.id
    is_admin = request.user.role == "admin"
    if not is_owner and (owner_only or not is_admin):
        raise PermissionDenied("This is not your attempt.")
    return attempt


class AttemptListCreateView(APIView):
    def get(self, request):
        qs = Attempt.objects.select_related("course")     # avoids N+1
        if request.user.role != "admin":
            qs = qs.filter(user=request.user)
        return Response(AttemptSerializer(qs, many=True).data)

    def post(self, request):
        ser = StartAttemptSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        course = get_object_or_404(Course, pk=ser.validated_data["course_id"], is_published=True)
        attempt, created = Attempt.objects.get_or_create(
            user=request.user, course=course, status="in_progress"
        )
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(AttemptSerializer(attempt).data, status=code)


class AttemptDetailView(APIView):
    def get(self, request, pk):
        attempt = get_attempt_for(request, pk)
        data = AttemptSerializer(attempt).data
        if attempt.status != "finished":
            return Response(data)          # no answers shown before finishing
        answers = attempt.answers.select_related("question")
        data["review"] = [
            {
                "question": a.question.text,
                "options": a.question.options,
                "selected_index": a.selected_index,
                "correct_index": a.question.correct_index,
                "is_correct": a.is_correct,
                "explanation": a.question.explanation,
            }
            for a in answers
        ]
        return Response(data)


class AttemptAnswerView(APIView):
    def post(self, request, pk):
        attempt = get_attempt_for(request, pk, owner_only=True)
        if attempt.status == "finished":
            return Response({"detail": "Attempt is already finished."}, status=400)

        ser = AnswerInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        qid = ser.validated_data["question_id"]
        idx = ser.validated_data["selected_index"]

        question = Question.objects.filter(pk=qid, course_id=attempt.course_id).first()
        if question is None:
            return Response({"detail": "Question does not belong to this course."}, status=400)
        if idx >= len(question.options):
            return Response({"detail": "selected_index is out of range."}, status=400)
        if Answer.objects.filter(attempt=attempt, question=question).exists():
            return Response({"detail": "Question already answered."}, status=400)

        Answer.objects.create(
            attempt=attempt, question=question,
            selected_index=idx, is_correct=(idx == question.correct_index),
        )
        return Response({"detail": "Answer saved."}, status=201)   # don't reveal is_correct


class AttemptFinishView(APIView):
    def post(self, request, pk):
        get_attempt_for(request, pk, owner_only=True)       # ownership check
        with transaction.atomic():
            attempt = Attempt.objects.select_for_update().get(pk=pk)   # lock the row
            if attempt.status == "finished":
                return Response({"detail": "Attempt is already finished."}, status=400)
            total = attempt.course.questions.count()
            correct = attempt.answers.filter(is_correct=True).count()
            attempt.score = round(correct / total * 100, 1) if total else 0
            attempt.status = "finished"
            attempt.finished_at = timezone.now()
            attempt.save()
        return Response(AttemptSerializer(attempt).data)