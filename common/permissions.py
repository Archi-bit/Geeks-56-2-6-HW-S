from datetime import timedelta
from django.utils import timezone
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsAnonymous(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class CanEditWithin15Minutes(BasePermission):
    def has_object_permission(self, request, view, obj):
        time_passed = timezone.now() - obj.created_at
        return time_passed <= timedelta(minutes=30)


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.is_staff:
            return False
        if request.method == 'POST':
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return True