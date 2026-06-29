from django.shortcuts import render

def home(request):
    return render(request, 'city/home.html', {'title': 'Главная'})

def news(request, extra=None):
    # extra будет содержать часть URL после /news/ (например, "satisfaction")
    # Если extra есть — можно его использовать (логировать, выводить в шаблон и т.п.)
    context = {
        'title': 'Новости города',
        'extra': extra,
    }
    return render(request, 'city/news.html', context)

def management(request, extra=None):
    context = {
        'title': 'Руководство города',
        'extra': extra,
    }
    return render(request, 'city/management.html', context)

def facts(request, extra=None):
    context = {
        'title': 'Факты о городе',
        'extra': extra,
    }
    return render(request, 'city/facts.html', context)

def contacts(request, extra=None):
    context = {
        'title': 'Контактные телефоны городских служб',
        'extra': extra,
    }
    return render(request, 'city/contacts.html', context)

def history(request, extra=None):
    # Для основного раздела истории
    context = {
        'title': 'История города',
        'extra': extra,
        'is_history_main': True,
        'is_history_people': False,
        'is_history_photos': False,
    }
    return render(request, 'city/history.html', context)

def history_people(request, extra=None):
    context = {
        'title': 'Известные жители Новочебоксарска',
        'extra': extra,
        'is_history_main': False,
        'is_history_people': True,
        'is_history_photos': False,
    }
    return render(request, 'city/history_people.html', context)

def history_photos(request, extra=None):
    context = {
        'title': 'Исторические фотографии Новочебоксарска',
        'extra': extra,
        'is_history_main': False,
        'is_history_people': False,
        'is_history_photos': True,
    }
    return render(request, 'city/history_photos.html', context)