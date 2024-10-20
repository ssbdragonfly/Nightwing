from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    join_code = models.IntegerField(
        unique=True,
        null=True,
        validators=[MinValueValidator(100000), MaxValueValidator(999999)],
    )
    started = models.BooleanField(default=False)
    current_question = models.PositiveIntegerField(default=1)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes"
    )

    def __str__(self):
        return self.title

    @property
    def finished(self) -> bool:
        return self.current_question > self.questions.count()

    def calculate_score(self, user):
        total = self.questions.count()
        correct = Answer.objects.filter(
            question__quiz=self, user=user, answer=models.F("question__correct_option")
        ).count()

        return correct, total


class MultipleChoiceQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField(max_length=200, default="")
    question_number = models.PositiveIntegerField(default=0)
    option_a = models.CharField(max_length=200, default="")
    option_b = models.CharField(max_length=200, default="")
    option_c = models.CharField(max_length=200, default="")
    option_d = models.CharField(max_length=200, default="")
    correct_option = models.CharField(
        max_length=1,
        choices=[("A", "Option A"), ("B", "Option B"), ("C", "Option C"), ("D", "Option D")],
        default="A",
    )

    def __str__(self):
        return self.question


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(
        MultipleChoiceQuestion, on_delete=models.CASCADE, related_name="answers"
    )
    answer = models.CharField(
        max_length=1,
        choices=[("A", "Option A"), ("B", "Option B"), ("C", "Option C"), ("D", "Option D")],
        default="A",
    )

    def __str__(self):
        return f"{self.user} answered {self.answer} for {self.question}"
