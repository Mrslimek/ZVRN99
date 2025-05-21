import json
from datetime import datetime
from django.conf import settings
from .models import ReceivedDataORM


def validate_and_parse_json_file_data(model_data: dict, index: int):
    """
    Валидация и парсинг одиночной записи.
    Возвращает кортеж: (список ошибок, name, parsed_date)
    """
    errors = []
    name = model_data.get("name")
    date_str = model_data.get("date")

    if not name:
        errors.append("Поле 'name' обязательно")
    elif len(name) > settings.MAX_NAME_LENGTH:
        errors.append(f"Поле 'name' не должно превышать {settings.MAX_NAME_LENGTH} символов).")

    if not date_str:
        errors.append("Поле 'date' обязательно")
    else:
        try:
            parsed_date = datetime.strptime(date_str, settings.DATE_FORMAT)
        except ValueError:
            errors.append(f"Поле 'date' должно быть в формате {settings.DATE_FORMAT}")
            parsed_date = None

    return errors, name, parsed_date


def process_upload_file(file_obj: bytes):
    """
    Обрабатывает загруженный файл и возвращает кортеж (records, errors):
     - records: список экземпляров Record, готовых для bulk_create,
     - errors: список сообщений об ошибках, если таковые имеются.
    """
    errors = []
    model_instances = []
    try:
        read_data = json.load(file_obj)
    except json.JSONDecodeError:
        errors.append("Невозможно обработать файл")
        return model_instances, errors

    if not isinstance(read_data, list):
        errors.append("Ожидается массив")
        return model_instances, errors

    for index, item in enumerate(read_data):
        model_data_errors, name, date = validate_and_parse_json_file_data(item, index)
        if model_data_errors:
            errors.extend(model_data_errors)
            continue

        model_instance = ReceivedDataORM(name=name, date=date)
        model_instances.append(model_instance)

    return model_instances, errors
