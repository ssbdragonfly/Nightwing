from django.shortcuts import render, redirect
from .forms import QuizForm

def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz:quiz_list')  
    else:
        form = QuizForm()
    return render(request, 'quiz/create_quiz.html', {'form': form})
