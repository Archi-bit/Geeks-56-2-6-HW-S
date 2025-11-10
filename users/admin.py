from django.contrib import admin
from users.models import CustomUser, ConfirmationCode
from django.contrib.auth.admin import UserAdmin


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "is_active",
        "is_staff",
        "registration_source",
        "last_login",
    )
    list_filter = ("is_active", "is_staff", "registration_source")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "phone_number", "birthdate")}),
        ("Статус и источник", {"fields": ("is_active", "is_staff", "registration_source", "last_login")}),
        ("Права доступа", {"fields": ("groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "phone_number", "first_name", "last_name"),
            },
        ),
    )


@admin.register(ConfirmationCode)
class ConfirmationCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at")
    search_fields = ("user__email", "code")