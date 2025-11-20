from django.db import transaction
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegisterValidateSerializer,
    AuthValidateSerializer,
    ConfirmationSerializer,
)
from users.tasks import send_otp_email
from users.models import CustomUser
import random
import string
from users.serializers import CustomTokenObtainPairSerializer
from common.redis import set_confirmation_code, check_and_delete_confirmation_code

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class AuthorizationAPIView(CreateAPIView):
    serializer_class = AuthValidateSerializer

    def post(self, request):
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        if user:
            if not user.is_active:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={'error': 'User account is not activated yet!'}
                )

            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={'key': token.key})

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={'error': 'User credentials are wrong!'}
        )

class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                is_active=False
            )

            code = ''.join(random.choices(string.digits, k=6))

            set_confirmation_code(user.id, code)

        send_otp_email.delay(email, code)

        return Response(
            status=status.HTTP_201_CREATED,
            data={
                'user_id': user.id,
                'confirmation_code': code
            }
        )

class ConfirmUserAPIView(CreateAPIView):
    serializer_class = ConfirmationSerializer

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        provided_code = serializer.validated_data['code']

        result = check_and_delete_confirmation_code(user_id, provided_code)
        if result == -1:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Код подтверждения не найден или истёк!'})
        if result == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Неверный код подтверждения!'})

        with transaction.atomic():
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Пользователь не найден'})

            user.is_active = True
            user.save()

            token, _ = Token.objects.get_or_create(user=user)

        return Response(
            status=status.HTTP_200_OK,
            data={
                'message': 'Аккаунт успешно активирован',
                'key': token.key
            }
        )