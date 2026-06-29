from django.http import HttpResponse
from datetime import datetime, date, timedelta
from django.shortcuts import render

def programmers_day(request):
    year = date.today().year
    # 1 января этого года
    start_of_year = date(year, 1, 1)
    # 256‑й день: прибавляем 255 дней к 1 января (потому что 1 января — это день 1)
    programmers_day = start_of_year + timedelta(days=255)

    is_today = (date.today() == programmers_day)

    context = {
        "year": year,
        "programmers_day": programmers_day,
        "is_today": is_today,
    }
    return render(request, "core/programmers_day.html", context)

def multiplication_table(request):
    range_1_10 = list(range(1, 11))
    table_rows = []

    for i in range_1_10:
        row_values = [i * j for j in range_1_10]
        table_rows.append({
            "multiplier": i,
            "values": row_values,
        })

    context = {
        "range_1_10": range_1_10,
        "table_rows": table_rows,
    }
    return render(request, "core/multiplication_table.html", context)


def home(request):
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return HttpResponse(f"Текущая дата и время: {formatted_time}")
