from django.urls import path

from . import views


app_name = "quiz"

urlpatterns = [
    path("", views.quiz_index, name="index"),
    path("create", views.create_quiz, name="create"),
    path("<int:quiz_id>/create_question", views.create_question_view, name="create_question"),
]
