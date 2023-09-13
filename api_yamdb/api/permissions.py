from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit it.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAdminOrAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow admin to edit,
    authenticated users to post,
    and others to read-only.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (
            request.user.is_staff or request.user.is_authenticated)


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object or admins to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
