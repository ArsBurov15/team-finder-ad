from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    PermissionsMixin,
    AbstractBaseUser,
)

from users.constants import (
    NAME_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ABOUT_MAX_LENGTH,
)
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя"""

    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Имя'
    )
    surname = models.CharField(
        max_length=SURNAME_MAX_LENGTH,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        verbose_name='Аватар'
    )
    about = models.TextField(
        blank=True,
        max_length=ABOUT_MAX_LENGTH,
        verbose_name='О себе'
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        unique=True,
        null=True,
        verbose_name='Телефон'
    )
    github_url = models.URLField(
        blank=True,
        verbose_name='Github'
    )
    is_active = models.BooleanField(
        default=True, verbose_name='Активен'
    )
    is_staff = models.BooleanField(
        default=False, verbose_name='Персонал'
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата регистрации'
    )

    favorites = models.ManyToManyField(
        'projects.Project',
        blank=True,
        related_name='interested_users',
        verbose_name='Избранные проекты'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.name} {self.surname}'

    def get_full_name(self):
        return f'{self.name} {self.surname}'
