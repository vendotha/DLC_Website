from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tutorials/', views.tutorials, name='tutorials'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('feedback/', views.feedback, name='feedback'),
]