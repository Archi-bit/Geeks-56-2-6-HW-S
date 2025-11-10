from datetime import date
from rest_framework.exceptions import ValidationError

def validate_user_age_from_token(request):
    # достаём birthdate из токена
    birthdate = request.auth.payload.get('birthdate') if hasattr(request, 'auth') else None

    if not birthdate:
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    # преобразуем строку в дату
    birthdate = date.fromisoformat(birthdate)
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
