from django import forms

from .models import MultipleChoiceQuestion, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title"]
        labels = {"title": "Quiz Title"}


class MultipleChoiceQuestionForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceQuestion
        fields = ["question"]
