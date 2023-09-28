from django.contrib.auth import get_user_model
from rest_framework import permissions

Roles = get_user_model().Roles


class IsSafeMethod(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS)


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user or (
            request.user.role in [Roles.MODERATOR, Roles.ADMIN]))


class IsAdminOrSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.role == Roles.ADMIN or request.user.is_superuser)
