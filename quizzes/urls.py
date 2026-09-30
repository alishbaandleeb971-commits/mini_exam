from django.urls import path
from .views import (
    AttemptListCreateView, AttemptDetailView, AttemptAnswerView, AttemptFinishView,
)

urlpatterns = [
    path("", AttemptListCreateView.as_view()),
    path("<int:pk>/", AttemptDetailView.as_view()),
    path("<int:pk>/answer/", AttemptAnswerView.as_view()),
    path("<int:pk>/finish/", AttemptFinishView.as_view()),
]