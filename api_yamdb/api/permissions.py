from rest_framework.permissions import SAFE_METHODS, BasePermission

from reviews.models import User


class IsAuthorOrReadOnly(BasePermission):
    """Permiss any action to the author or reading to any user."""

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)


class IsAdminOrAuthorOrReadOnly(BasePermission):
    """Allow any action to the author and administrator or read to any user."""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_superuser
                or request.user.is_staff)


class CustomAdminPermission(BasePermission):
    """Allow any action to the administrator."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == User.ADMIN
                     or request.user.is_superuser))


class SafeMethodAdminPermission(BasePermission):
    """Allow any action to the administrator or read to any user."""

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_superuser))

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.role == User.ADMIN
                         or request.user.is_superuser)))
