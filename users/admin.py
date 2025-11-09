from django.contrib import admin
from django.utils.text import phone2numeric

from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "phone_number", "is_active", 'birthdate')
    fieldsets = (
        (None, {"fields": ("email", "password", "phone_number", "is_active", "birthdate")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
        ("important dates", {"fields": ("last_login",)})
    )
    ordering = ("email",)