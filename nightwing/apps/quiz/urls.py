from django.urls import path

from . import views

app_name = "quiz"

urlpatterns = [
    path("<int:quiz_id>/", views.quiz_index, name="index"),
    path("", views.list_quizzes, name="list"),
    path("create", views.create_quiz, name="create"),
    path("<int:quiz_id>/create_question", views.create_question_view, name="create_question"),
    path("<int:quiz_id>/start", views.start_quiz, name="start"),
    path("quiz/<int:join_code>/", views.join_quiz, name="join"),
    path("quiz/<int:quiz_id>/question", views.get_question, name="get_question"),
    path(
        "quiz/<int:quiz_id>/answer/<int:question_id>/<int:user_id>",
        views.submit_answer_to_quiz,
        name="answer_question",
    ),
    path(
        "quiz/<int:quiz_id>/<int:question_number>",
        views.passthrough_questions,
        name="passthrough",
    ),
]
