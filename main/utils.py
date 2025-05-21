from django.forms import ValidationError
from datetime import datetime


def name_validator(key: str, value: str) -> dict | ValidationError:
    if len(value) >= 50:
        return ValidationError(f"Поле {key} должно быть менее 50 символов")
    else:
        return {key: value}


def date_validator(key: str, value: str) -> dict | ValidationError:
    try:
        value = datetime.strptime(value, "%Y-%m-%d_%H:%M")
        return {key: value}
    except ValueError:
        return ValidationError(f"Поле {key} должно быть в формате 'YYYY-MM-DD_HH:mm'")
