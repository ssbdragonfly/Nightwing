from django.urls import path

from . import views


app_name = 'quiz'

urlpatterns = [
    path('create', views.create_quiz, name='create'),
]
