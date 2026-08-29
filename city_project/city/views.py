from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from .utils import get_or_create_sa_user, is_admin as _is_admin, calculate_ban_until
from .models import Article, Comment, SiteSettings, User as SAUser
from .database import SessionLocal

def is_admin_wrapper(user):
    return _is_admin(user)

# --- Старые страницы (с поддержкой dynamic styles) ---

def home(request):
    db = SessionLocal()
    try:
        settings = db.query(SiteSettings).first()
        if settings is None:
            settings = SiteSettings(background_color="#ffffff", font_color="#000000", font_size_px=16)
            db.add(settings)
            db.commit()
        articles = db.query(Article).order_by(Article.created_at.desc()).limit(5).all()
        return render(request, 'city/home.html', {'title': 'Главная', 'articles': articles, 'settings': settings})
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def news(request, extra=None):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
    context = {
        'title': 'Новости города',
        'extra': extra,
        'settings': settings,
    }
    return render(request, 'city/news.html', context)

def management(request, extra=None):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
    context = {
        'title': 'Руководство города',
        'extra': extra,
        'settings': settings,
    }
    return render(request, 'city/management.html', context)

def facts(request, extra=None):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
    context = {
        'title': 'Факты о городе',
        'extra': extra,
        'settings': settings,
    }
    return render(request, 'city/facts.html', context)

def contacts(request, extra=None):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
    context = {
        'title': 'Контактные телефоны городских служб',
        'extra': extra,
        'settings': settings,
    }
    return render(request, 'city/contacts.html', context)

def history(request, extra=None):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
    context = {
        'title': 'История города',
        'extra': extra,
        'is_history_main': True,
        'is_history_people': False,
        'is_history_photos': False,
        'settings': settings,
    }
    return render(request, 'city/history.html', context)

def history_people(request, extra=None):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
    context = {
        'title': 'Известные жители Новочебоксарска',
        'extra': extra,
        'is_history_main': False,
        'is_history_people': True,
        'is_history_photos': False,
        'settings': settings,
    }
    return render(request, 'city/history_people.html', context)

def history_photos(request, extra=None):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
    context = {
        'title': 'Исторические фотографии Новочебоксарска',
        'extra': extra,
        'is_history_main': False,
        'is_history_people': False,
        'is_history_photos': True,
        'settings': settings,
    }
    return render(request, 'city/history_photos.html', context)


# --- Новые страницы: статьи и админка ---

@login_required
def news_list(request):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
        articles = db.query(Article).order_by(Article.created_at.desc()).all()
    return render(request, 'city/news.html', {'title': 'Новости города', 'articles': articles, 'settings': settings})

@login_required
def article_detail(request, pk):
    with SessionLocal() as db:
        article = db.query(Article).get(pk)
        settings = db.query(SiteSettings).first() or SiteSettings()
        if article:
            article.views_count += 1
            db.commit()
    return render(request, 'city/article_detail.html', {'article': article, 'settings': settings})

@login_required
@user_passes_test(is_admin_wrapper, login_url='/accounts/login/')
def admin_dashboard(request):
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
        users = db.query(SAUser).all()
        articles = db.query(Article).all()
        stats_views = db.query(Article).order_by(Article.views_count.desc()).limit(5).all()
        stats_comments = db.query(Article).order_by(Article.comments_count.desc()).limit(5).all()
        stats_saves = db.query(Article).order_by(Article.saves_count.desc()).limit(5).all()
    return render(request, 'city/admin_dashboard.html', {
        'title': 'Админ-панель',
        'settings': settings,
        'users': users,
        'articles': articles,
        'stats_views': stats_views,
        'stats_comments': stats_comments,
        'stats_saves': stats_saves,
    })

@login_required
@user_passes_test(is_admin_wrapper)
def ban_user(request, user_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Только POST")
    duration = request.POST.get('duration')
    reason = request.POST.get('reason', '')
    with SessionLocal() as db:
        user = db.query(SAUser).get(user_id)
        if not user:
            return HttpResponseForbidden("Пользователь не найден")
        user.is_banned = True
        user.banned_until = calculate_ban_until(duration)
        user.ban_reason = reason
        db.commit()
    messages.success(request, f"Пользователь {user.username} забанен.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin_wrapper)
def unban_user(request, user_id):
    with SessionLocal() as db:
        user = db.query(SAUser).get(user_id)
        if user:
            user.is_banned = False
            user.banned_until = None
            user.ban_reason = None
            db.commit()
            messages.success(request, f"Пользователь {user.username} разбанен.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin_wrapper)
def update_site_settings(request):
    if request.method != 'POST':
        return HttpResponseForbidden("Только POST")
    bg = request.POST.get('background_color', '#ffffff')
    font = request.POST.get('font_color', '#000000')
    size = int(request.POST.get('font_size_px', 16))
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first()
        if not settings:
            settings = SiteSettings()
            db.add(settings)
        settings.background_color = bg
        settings.font_color = font
        settings.font_size_px = size
        db.commit()
    messages.success(request, "Настройки сайта обновлены.")
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin_wrapper)
def create_article(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        author = get_or_create_sa_user(request.user)
        with SessionLocal() as db:
            article = Article(title=title, content=content, author_id=author.id)
            db.add(article)
            db.commit()
        messages.success(request, "Статья опубликована.")
        return redirect('news_list')
    with SessionLocal() as db:
        settings = db.query(SiteSettings).first() or SiteSettings()
    return render(request, 'city/create_article.html', {'title': 'Создать статью', 'settings': settings})

