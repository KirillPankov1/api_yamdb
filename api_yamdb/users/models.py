from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from api_yamdb.settings import NUMBER_OF_VALUES
from core.utils import get_confirmation_code

MAX_LEN_ROLE = 10
MAX_LEN_BIO = 500


class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"

    email = models.EmailField(max_length=NUMBER_OF_VALUES,
                              blank=False,
                              unique=True)
    role = models.CharField(max_length=MAX_LEN_ROLE,
                            choices=Roles.choices,
                            default=Roles.USER)
    bio = models.TextField(max_length=MAX_LEN_BIO, blank=True)
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

    confirmation_code = models.TextField(blank=False,
                                         default=get_confirmation_code())

    class Meta:
        verbose_name = ('custom user')
        verbose_name_plural = ('custom users')
