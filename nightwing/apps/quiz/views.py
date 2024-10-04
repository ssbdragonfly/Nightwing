import contextlib
import random

from django import http
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import MultipleChoiceQuestionForm, QuestionForm, QuizForm
from .models import MultipleChoiceQuestion, Quiz


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
            question.question_number = quiz.questions.count() + 1
            question.save()
            return redirect("quiz:index", quiz_id=quiz.id)
    else:
        form = MultipleChoiceQuestionForm()
    return render(request, "quiz/create_question.html", {"form": form, "quiz": quiz})


@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    unique = False
    while not unique:
        with contextlib.suppress(IntegrityError):
            quiz.join_code = random.randint(100000, 999999)
            quiz.started = True
            quiz.save(update_fields=["join_code", "started"])
            unique = True

    return render(request, "quiz/start_quiz.html", {"quiz": quiz})


def passthrough_questions(request, quiz_id, question_number):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.current_question = question_number
    quiz.save(update_fields=["current_question"])
    return render(
        request,
        "quiz/question.html",
        {
            "quiz": quiz,
            "next_question": quiz.current_question + 1,
            "total_questions": quiz.questions.count(),
        },
    )


@csrf_exempt
def join_quiz(request, join_code):
    quiz = get_object_or_404(Quiz, join_code=join_code)
    return JsonResponse({"quiz_id": quiz.id})


@csrf_exempt
def get_question(request, quiz_id: int):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method != "POST" or not quiz.started:
        raise http.Http404
    question = quiz.questions.get(question_number=quiz.current_question)
    return JsonResponse(
        {
            "question": question.question,
            "option_a": question.option_a,
            "option_b": question.option_b,
            "option_c": question.option_c,
            "option_d": question.option_d,
        }
    )


@csrf_exempt
def submit_answer_to_quiz(request, quiz_id, question_id, user_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = get_object_or_404(User, id=user_id)
    if request.method != "POST":
        raise http.Http404

    form = QuestionForm(request.POST)
    if form.is_valid():
        answer = form.cleaned_data["answer"]
        question = MultipleChoiceQuestion.objects.get(id=question_id, quiz=quiz)
        question.answers.create(answer=answer, user=user)
        return JsonResponse({"message": "Success!"})
    return JsonResponse({"errors": form.errors.as_json()}, status=400, reason="Invalid POST data")
