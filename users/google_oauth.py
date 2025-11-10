import os
import requests
from django.utils import timezone
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from users.serializers import OauthCodeSerializer

User = get_user_model()


class GoogleLoginApiView(CreateAPIView):
    serializer_class = OauthCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        token_response = requests.post(
            url="https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),
                "grant_type": "authorization_code",
            },
        )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return Response(
                {"error": "Invalid access_token", "details": token_data},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_info = requests.get(
            url="https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

        print("Google user info:", user_info)

        email = user_info.get("email")
        given_name = user_info.get("given_name")
        family_name = user_info.get("family_name")

        if not email:
            return Response({"error": "Email not provided by Google"}, status=400)

        user, created = User.objects.get_or_create(email=email)

        user.first_name = given_name
        user.last_name = family_name
        user.is_active = True
        user.registration_source = "google"
        user.last_login = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["first_name"] = user.first_name
        refresh["last_name"] = user.last_name
        refresh["registration_source"] = user.registration_source

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "registration_source": user.registration_source,
                "last_login": user.last_login,
            },
            status=status.HTTP_200_OK,
        )