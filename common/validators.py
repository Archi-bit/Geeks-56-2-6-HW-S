from datetime import date
from rest_framework.exceptions import ValidationError

def validate_user_age_from_token(request):
    token_data = getattr(request, "auth", None)
    if not token_data:
        raise ValidationError("Токен не найден.")

    birthdate_str = token_data.get("birthdate")
    if not birthdate_str:
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    try:
        birthdate = date.fromisoformat(birthdate_str)
    except ValueError:
        raise ValidationError("Некорректный формат даты рождения.")

    today = date.today()
    age = today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
