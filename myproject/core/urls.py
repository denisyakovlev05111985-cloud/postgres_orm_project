from django.urls import path
from core import views

urlpatterns = [
    path('programmers-day/', views.programmers_day, name='programmers_day'),
]
