from django.contrib import admin

from .models import MultipleChoiceQuestion, Quiz

admin.site.register(Quiz)
admin.site.register(MultipleChoiceQuestion)
