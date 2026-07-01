from django.urls import path
from . import views

urlpatterns = [
    path('', views.song_line, {'lang': 'en'}, name='song_en'),
    path('fr/', views.song_line, {'lang': 'fr'}, name='song_fr'),
    path('de/', views.song_line, {'lang': 'de'}, name='song_de'),
    path('es/', views.song_line, {'lang': 'es'}, name='song_es'),
]
