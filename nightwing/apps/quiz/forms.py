from django import forms

from .models import Answer, MultipleChoiceQuestion, Quiz


class QuizForm(forms.ModelForm):
    use_ai = forms.BooleanField(required=False, label="Use AI to generate questions")
    num_questions = forms.IntegerField(min_value=1, max_value=10, initial=5, label="Number of questions")
    topic = forms.CharField(max_length=200, required=False, label="Quiz topic (for AI-generated questions)")

    class Meta:
        model = Quiz
        fields = ["title", "use_ai", "num_questions", "topic"]
        labels = {"title": "Quiz Title"}


class MultipleChoiceQuestionForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceQuestion
        fields = ["question", "option_a", "option_b", "option_c", "option_d", "correct_option"]


class QuestionForm(forms.Form):
    class Meta:
        model = Answer
        fields = ["answer"]
