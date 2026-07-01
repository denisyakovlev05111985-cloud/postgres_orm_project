from django.shortcuts import render

def song_line(request, lang='en'):
    lines = {
        'en': {
            'line': 'We are the champions, my friends',
            'author': 'Queen — We Are The Champions',
            'lang_name': 'English'
        },
        'fr': {
            'line': "Nous sommes les champions, mes amis",
            'author': 'Queen — Nous Sommes Les Champions',
            'lang_name': 'Français'
        },
        'de': {
            'line': 'Wir sind die Meister, meine Freunde',
            'author': 'Queen — Wir Sind Die Meister',
            'lang_name': 'Deutsch'
        },
        'es': {
            'line': 'Somos los campeones, mis amigos',
            'author': 'Queen — Somos Los Campeones',
            'lang_name': 'Español'
        }
    }

    # Если язык не найден, по умолчанию английский
    context = lines.get(lang, lines['en'])
    context['current_lang'] = lang
    return render(request, 'songs/song.html', context)
