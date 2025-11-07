from rest_framework import serializers
# from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from users.models import CustomUser, ConfirmationCode
from django.contrib.auth import authenticate


class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AuthValidateSerializer(UserBaseSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError("Неверные учетные данные!")
        if not user.is_active:
            raise ValidationError("Пользователь не активирован")

        attrs["user"] = user
        return attrs


class RegisterValidateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Номер телефона (необьязательно для обычного пользователя)"
    )

    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким именем уже существует!")
        return email

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        code = attrs.get('code')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError('Пользователь не существует!')

        try:
            confirmation_code = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise ValidationError('Код подтверждения не найден!')

        if confirmation_code.code != code:
            raise ValidationError('Неверный код подтверждения!')

        return attrs