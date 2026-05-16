import hashlib
import pathlib
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager,
    PermissionsMixin,
    AbstractBaseUser,
)
from .constants import (
    NAME_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ABOUT_MAX_LENGTH,
    AVATAR_COLORS,
    AVATAR_SIZE,
    AVATAR_TEXT_SIZE,
    AVATAR_FONT_PATH,
)


class UserManager(BaseUserManager):
    """Менеджер пользователей"""

    def create_user(
        self,
        email,
        name,
        surname,
        phone=None,
        password=None,
        **extras
    ):
        if not email:
            raise ValueError('Укажите email')
        if not name:
            raise ValueError('Укажите ваше имя')
        if not surname:
            raise ValueError('Укажите вашу фамилию')
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            surname=surname,
            phone=phone,
            **extras
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        name,
        surname,
        phone=None,
        password=None,
        **extras
    ):
        extras.setdefault('is_staff', True)
        extras.setdefault('is_superuser', True)
        extras.setdefault('is_active', True)
        return self.create_user(
            email, name, surname, phone, password, **extras
        )


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

    def generate_avatar_image(self):
        """Создание аватарки на основе имени пользователя"""

        raw_name = getattr(self, 'name', None) or ''
        letter = (raw_name.strip() or 'U')[0].upper()

        if self.pk:
            seed = self.pk
        else:
            hash_bytes = hashlib.blake2b(
                (self.email or 'user').encode('utf-8'),
                digest_size=4
            ).digest()
            seed = int.from_bytes(hash_bytes, byteorder='big')

        color_index = seed % len(AVATAR_COLORS)
        bg_color = AVATAR_COLORS[color_index]

        image = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), bg_color)
        draw = ImageDraw.Draw(image)

        font_path = pathlib.Path(settings.BASE_DIR) / AVATAR_FONT_PATH

        try:
            font = ImageFont.truetype(str(font_path), AVATAR_TEXT_SIZE)
        except (IOError, OSError):
            font = ImageFont.load_default()

        center = AVATAR_SIZE // 2
        draw.text(
            (center, center),
            letter,
            fill='white',
            font=font,
            anchor='mm'
        )
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        email_slug = self.email.split('@')[0] if self.email else 'user'
        filename = f'avatar_{email_slug}_{letter}.png'
        return ContentFile(buffer.getvalue(), name=filename)
