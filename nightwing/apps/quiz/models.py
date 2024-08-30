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

    def __str__(self):
        return self.title


class MultipleChoiceQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField(max_length=200, default="")   
    option_a = models.CharField(max_length=200, default="")
    option_b = models.CharField(max_length=200, default="")
    option_c = models.CharField(max_length=200, default="")
    option_d = models.CharField(max_length=200, default="")
    correct_option = models.CharField(max_length=1, choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')], default="A")

    def __str__(self):
        return self.question
