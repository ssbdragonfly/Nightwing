import contextlib
import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db import IntegrityError

from .forms import MultipleChoiceQuestionForm, QuizForm
from .models import Quiz


@login_required
def quiz_index(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()  
    return render(request, "quiz/view_quiz.html", {"quiz": quiz, "questions": questions})


@login_required
def create_quiz(request):
    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            return redirect("quiz:index", quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, "quiz/create_quiz.html", {"form": form})


@login_required
def create_question_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        form = MultipleChoiceQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect("quiz:index", args=[quiz.id])
    else:
        form = MultipleChoiceQuestionForm()
    return render(request, "quiz/create_question.html", {"form": form})


@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    unique = False
    while not unique:
        with contextlib.suppress(IntegrityError):
            quiz.join_code = random.randint(100000, 999999)
            quiz.save(update_fields=["join_code"])
            unique = True

    return render(request, "quiz/start_quiz.html", {"quiz": quiz})
