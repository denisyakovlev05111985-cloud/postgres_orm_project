from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.news, name='news'),
    path('management/', views.management, name='management'),
    path('facts/', views.facts, name='facts'),
    path('contacts/', views.contacts, name='contacts'),
    path('history/', views.history, name='history'),
    path('history/people/', views.history_people, name='history_people'),
    path('history/photos/', views.history_photos, name='history_photos'),

    # Страницы для авторизованных
    path('news-list/', views.news_list, name='news_list'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    
    # Админка и действия
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('ban-user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('unban-user/<int:user_id>/', views.unban_user, name='unban_user'),
    path('update-site-settings/', views.update_site_settings, name='update_site_settings'),
    path('create-article/', views.create_article, name='create_article'),
]
