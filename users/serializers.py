from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["birthdate"] = str(user.birthdate) if user.birthdate else None
        return token

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
        help_text="Номер телефона (необязательно для обычного пользователя)"
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

    def validate_user_id(self, value):
        try:
            CustomUser.objects.get(id=value)
        except CustomUser.DoesNotExist:
            raise ValidationError('Пользователь не существует!')
        return value

    def validate_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise ValidationError('Код должен состоять из 6 цифр!')
        return value

class OauthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
