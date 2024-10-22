from django.contrib import admin

from .models import Answer, MultipleChoiceQuestion, Quiz

admin.site.register(Quiz)
admin.site.register(MultipleChoiceQuestion)
admin.site.register(Answer)
