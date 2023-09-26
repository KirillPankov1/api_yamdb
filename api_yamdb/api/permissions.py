from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from rest_framework import permissions

Roles = get_user_model().Roles


class IsSafeMethod(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS)
    

class IsModeratorOrHigher(permissions.BasePermission):

    def has_permission(self, request, view):
        return (hasattr(request.user, 'role') and request.user.role in [Roles.MODERATOR, Roles.ADMIN] or request.user.is_superuser)

    
class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit it.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (hasattr(request.user, 'role') and request.user.role == Roles.ADMIN))


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object or admins to edit it.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        print(obj.author.username, request.user.username )
        return (hasattr(request.user, 'role') and (obj.author == request.user or request.user.role in [Roles.MODERATOR, Roles.ADMIN]))


class IsAdminOrSuperUser(permissions.BasePermission):
    """
    Custom permission to only allow admin or superusers to access.
    """
    def has_permission(self, request, view):
        return (hasattr(request.user, 'role') and request.user.role == Roles.ADMIN
                ) or request.user.is_superuser



