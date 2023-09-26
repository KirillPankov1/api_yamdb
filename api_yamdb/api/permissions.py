from django.contrib.auth.models import AnonymousUser

from rest_framework import permissions

ROLE_ADMIN= 'admin'
ROLE_MODERATOR= 'moderator'
ROLE_USER = 'user'


class IsSafeMethod(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS)
    

class IsModeratorOrHigher(permissions.BasePermission):

    def has_permission(self, request, view):
        return (hasattr(request.user, 'role') and request.user.role in [ROLE_MODERATOR, ROLE_ADMIN] or request.user.is_superuser)

    
class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit it.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (hasattr(request.user, 'role') and request.user.role == ROLE_ADMIN))


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        print(obj.author, request.user )
        return hasattr(request.user, 'role') and (obj.author == request.user or request.user.role in [
            ROLE_MODERATOR, ROLE_ADMIN])


class IsAdminOrSuperUser(permissions.BasePermission):
    """
    Custom permission to only allow admin or superusers to access.
    """
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False

        return (hasattr(request.user, 'role') and request.user.role == ROLE_ADMIN
                ) or request.user.is_superuser or request.user.is_staff


class IsAdminOrSelf(permissions.BasePermission):
    """
    Custom permission to only allow
    admin or the user himself to access the object.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff

