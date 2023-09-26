from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from api.utils import get_confirmation_code


class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"

    role = models.CharField(max_length=10,
                            choices=Roles.choices,
                            default=Roles.USER)
    bio = models.TextField(max_length=500, blank=True)
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
        verbose_name=('groups')
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
        verbose_name=('user permissions'),
    )

    confirmation_code = models.TextField(blank = False, default = get_confirmation_code())

    class Meta:
        verbose_name = ('custom user')
        verbose_name_plural = ('custom users')
