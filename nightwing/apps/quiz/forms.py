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
        fields = ["question", "option_a", "option_b", "option_c", "option_d", "quiz"]
        labels = {
            "question": "Question",
            "option_a": "Option A",
            "option_b": "Option B",
            "option_c": "Option C",
            "option_d": "Option D",
            "quiz": "Quiz",
        }


class QuestionForm(forms.Form):
    answer = forms.ChoiceField(choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")])
