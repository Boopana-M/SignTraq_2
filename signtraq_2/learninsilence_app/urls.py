from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/', views.quiz, name='quiz'),
    path('converter/', views.converter, name='converter'),
    path('api/quiz-questions/', views.quiz_questions, name='quiz_questions'),
    path('api/save-quiz-result/', views.save_quiz_result, name='save_quiz_result'),
] 