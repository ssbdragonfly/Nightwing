import ast
import contextlib
import json
import logging
import random
from typing import Any

import google.generativeai as genai
from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from nightwing.apps.store.models import Credit

from .forms import MultipleChoiceQuestionForm, QuestionForm, QuizForm
from .models import Answer, MultipleChoiceQuestion, Quiz

logger = logging.getLogger(__name__)


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
            quiz = form.save(commit=False)
            quiz.owner = request.user
            quiz.save()
            quiz.save()

            if form.cleaned_data["use_ai"]:
                genai.configure(api_key="AIzaSyDngfpFX8fyBDAGMCvP6IFaedSBo6pfMlc")
                model = genai.GenerativeModel("gemini-pro")

                prompt = f"Create {form.cleaned_data['num_questions']} multiple-choice questions about {form.cleaned_data['topic']}. For each question, provide 4 options (A, B, C, D) and indicate the correct answer. Format the output as a Python list of dictionaries, where each dictionary represents a question with keys 'question', 'option_a', 'option_b', 'option_c', 'option_d', and 'correct_option'."

                response = model.generate_content(prompt)
                response_text = response.text.strip().lstrip("`").rstrip("`")
                if response_text.startswith("python\n"):
                    response_text = response_text[7:]

                try:
                    questions = json.loads(response_text)
                except json.JSONDecodeError:
                    try:
                        start = (
                            response_text.index("[")
                            if "[" in response_text
                            else response_text.index("{")
                        )
                        end = (
                            response_text.rindex("]")
                            if "]" in response_text
                            else response_text.rindex("}")
                        )
                        questions = ast.literal_eval(response_text[start : end + 1])
                    except (ValueError, SyntaxError) as e:
                        logging.error(f"Error parsing AI response: {e!s}")
                        messages.error(
                            request,
                            "An error occurred while generating questions. Please try again or create questions manually.",
                        )
                        quiz.delete()
                        return render(request, "quiz/create_quiz.html", {"form": form})

                if not isinstance(questions, list) or not all(
                    isinstance(q, dict) for q in questions
                ):
                    logging.error(f"Invalid question format: {questions}")
                    messages.error(
                        request,
                        "An error occurred while generating questions. Please try again or create questions manually.",
                    )
                    quiz.delete()
                    return render(request, "quiz/create_quiz.html", {"form": form})

                for i, q in enumerate(questions, start=1):
                    MultipleChoiceQuestion.objects.create(
                        quiz=quiz,
                        question_number=i,
                        question=q["question"],
                        option_a=q["option_a"],
                        option_b=q["option_b"],
                        option_c=q["option_c"],
                        option_d=q["option_d"],
                        correct_option=q["correct_option"],
                    )
                messages.success(request, "Quiz created successfully with AI-generated questions!")
            else:
                messages.success(request, "Quiz created successfully!")
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
    quiz.participants.clear()
    for q in quiz.questions.all():
        q.answers.all().delete()

    unique = False
    while not unique:
        with contextlib.suppress(IntegrityError):
            quiz.join_code = random.randint(100000, 999999)
            # reset any previous state
            quiz.started = True

            quiz.current_question = 1
            quiz.save(update_fields=["join_code", "started"])
            unique = True

    return redirect("quiz:passthrough", quiz_id=quiz.id, question_number=1)


@login_required
def passthrough_questions(request, quiz_id, question_number):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.current_question = question_number
    quiz.save(update_fields=["current_question"])
    if quiz.finished:
        return redirect("quiz:finish_quiz", quiz_id=quiz.id)
    question = get_object_or_404(quiz.questions, question_number=question_number)
    return render(
        request,
        "quiz/question.html",
        {
            "quiz": quiz,
            "question": question,
            "next_question": quiz.current_question + 1,
            "total_questions": quiz.questions.count(),
        },
    )


@login_required
def question_results(request, quiz_id, question_number):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(quiz.questions, question_number=question_number)
    data: dict[str, Any] = {
        "labels": ["A", "B", "C", "D"],
    }
    correct_idx = data["labels"].index(question.correct_option.upper())
    data["datasets"] = [
        {
            "label": "Responses",
            "data": [
                question.answers.filter(answer__iexact=answer).count() for answer in data["labels"]
            ],
            "borderWidth": 1,
            "backgroundColor": [
                ("rgba(75, 44, 50, 1)" if i != correct_idx else "rgba(210, 246, 246, 1)")
                for i in range(len(data["labels"]))
            ],
        }
    ]
    data["datasets"][0]["borderColor"] = data["datasets"][0]["backgroundColor"]
    data["base"] = 1
    correct_answer = question.correct_option.lower()
    return render(
        request,
        "quiz/question_results.html",
        {
            "question": question,
            "quiz": quiz,
            "answer_data": data,
            "correct_answer": correct_answer,
            "next_question": quiz.current_question + 1,
        },
    )


@login_required
def finish_quiz(request, quiz_id):
    quiz = get_object_or_404(
        Quiz.objects.annotate(question_count=models.Count("questions")), id=quiz_id
    )
    quiz.current_question = quiz.question_count + 1
    quiz.save(update_fields=["current_question"])
    return render(request, "quiz/finish_quiz.html", {"quiz": quiz})


@login_required
def list_quizzes(request):
    quizzes = request.user.quizzes.all()
    return render(request, "quiz/list_quizzes.html", {"quizzes": quizzes})


@csrf_exempt
def join_quiz(request, join_code):
    quiz = get_object_or_404(Quiz, join_code=join_code)
    return JsonResponse({"quiz_id": quiz.id})


@csrf_exempt
def get_question(request, quiz_id: int):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method != "POST" or not quiz.started:
        raise http.Http404

    if quiz.finished:
        data = {"message": "Quiz has finished!"}
        if request.POST.get("user"):
            user = get_object_or_404(User, username=request.POST["user"])
            data["correct"], data["total"] = quiz.calculate_score(user)
        return JsonResponse(data)

    question = quiz.questions.get(question_number=quiz.current_question)
    data: dict[str, Any] = {
        "question": question.question,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "id": question.id,
    }
    if user_id := request.POST.get("user"):
        user = get_object_or_404(User, username=user_id)
        answer = Answer.objects.filter(question=question, user=user).first()
        if answer is not None:
            data["correct"] = answer.answer == question.correct_option
    return JsonResponse(data)


@csrf_exempt
def submit_answer_to_quiz(request, quiz_id, question_id, username):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = get_object_or_404(User, username=username)
    question = get_object_or_404(
        quiz.questions,
        id=question_id,
    )
    if request.method != "POST":
        raise http.Http404

    form = QuestionForm(request.POST)
    if form.is_valid():
        old = Answer.objects.filter(question=question, user=user).all()
        old.delete()
        answer = form.save(commit=False)
        answer.question = question
        answer.user = user
        answer.save()
        if not old and answer.answer.lower() == question.correct_option.lower():
            credits = Credit.get_credit(user)
            credits.money = models.F("money") + question.credits
            credits.save(update_fields=["money"])
            quiz.participants.add(user)
        return JsonResponse({"message": "success"})
    return JsonResponse(
        {"message": "failure", "errors": form.errors.as_json()},
        status=400,
        reason="Invalid POST data",
    )
