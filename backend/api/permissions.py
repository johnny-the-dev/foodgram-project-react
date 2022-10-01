from rest_framework import permissions


class IsAuthorOrReadonly(permissions.BasePermission):
    def has_permission(self, request, view):
        if (
            request.method in permissions.SAFE_METHODS or
            request.user.is_authenticated
        ):
            return True

    def has_object_permission(self, request, view, obj):
        if (
            request.method in permissions.SAFE_METHODS or
            request.user == obj.author or
            request.user.is_admin or
            request.user.is_superuser
        ):
            return True
