from django.contrib.auth.models import AnonymousUser

from rest_framework import permissions

ROLE_ADMIN= 'admin'
ROLE_MODERATOR= 'moderator'
ROLE_USER = 'user'


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit it.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (hasattr(request.user, 'role') and request.user.role == ROLE_ADMIN))


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


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        print(f"Object: {obj}, User: {request.user}")
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.role in [
            ROLE_MODERATOR, ROLE_ADMIN]


class IsAdminOrAuthenticatedForList(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit,
    authenticated users to list, and others to read-only.
    """

    def has_permission(self, request, view):
        if view.action == 'list':
            if not request.user or not request.user.is_authenticated:
                return False
            return request.user.role == ROLE_ADMIN
        return True


class IsAdminOrSuperUserForDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (
            request.user.is_staff or request.user.is_superuser))


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


class IsAdminOrForbidden(permissions.BasePermission):
    """
    Custom permission to grant access only to admin users.
    """
    def has_permission(self, request, view):
        print(f"Inside IsAdminOrForbidden: {request.user.is_staff}")
        return bool(request.user and request.user.is_staff)


class IsAdminOrTargetUser(permissions.BasePermission):
    """
    Custom permission to only allow admin
    or the target user himself to access the object.
    """

    def has_permission(self, request, view):
        # Deny all non-authenticated users
        if not request.user or not request.user.is_authenticated:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Allow admins to retrieve any user
        if request.user.role == ROLE_ADMIN:
            return True

        # Allow users to retrieve only themselves
        return obj == request.user


# Add this if you need a strict authenticated or read-only class
class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


# Modify this to include 'user' role for editing their own posts
class IsAuthorOrUserOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.role in [ROLE_USER,
                                                                   ROLE_MODERATOR,
                                                                   ROLE_ADMIN]
