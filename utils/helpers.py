import datetime

def format_dt(dt: datetime.datetime):
    """Красивое форматирование даты и времени"""
    return dt.strftime('%d.%m.%Y %H:%M')

def clean_content(text: str):
    """Очистка текста от лишних пробелов и упоминаний @everyone"""
    return text.replace("@everyone", "@everyone (blocked)").strip()