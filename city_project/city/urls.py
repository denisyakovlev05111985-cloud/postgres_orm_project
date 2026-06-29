from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.news, name='news'),
    path('news/<str:extra>/', views.news, name='news_extra'),

    path('management/', views.management, name='management'),
    path('management/<str:extra>/', views.management, name='management_extra'),

    path('facts/', views.facts, name='facts'),
    path('facts/<str:extra>/', views.facts, name='facts_extra'),

    path('contacts/', views.contacts, name='contacts'),
    path('contacts/<str:extra>/', views.contacts, name='contacts_extra'),

    # История: подразделы (сначала конкретные)
    path('history/people/', views.history_people, name='history_people'),
    path('history/photos/', views.history_photos, name='history_photos'),

    # История: основной раздел + обработка любых суффиксов
    path('history/', views.history, name='history'),
    path('history/<str:extra>/', views.history, name='history_extra'),
]
