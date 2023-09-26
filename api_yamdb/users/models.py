from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', _('User')),
        ('moderator', _('Moderator')),
        ('admin', _('Admin')),
    )
    role = models.CharField(max_length=10,
                            choices=ROLE_CHOICES,
                            default='user')
    bio = models.TextField(max_length=500, blank=True)
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
        verbose_name=_('groups')
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
        verbose_name=_('user permissions'),
    )

    class Meta:
        verbose_name = _('custom user')
        verbose_name_plural = _('custom users')
