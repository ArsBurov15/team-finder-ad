import hashlib
import pathlib
import re
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.paginator import Paginator

from users.constants import (
    AVATAR_COLORS,
    AVATAR_SIZE,
    AVATAR_TEXT_SIZE,
    AVATAR_FONT_PATH,
    PHONE_DIGITS_LENGTH_1,
    PHONE_DIGITS_LENGTH_2,
    PHONE_START_DIGIT,
    PHONE_REPLACE_DIGIT,
)

User = get_user_model()


def validate_phone(phone, instance=None):
    """Валидация номера телефона."""

    if not phone or not phone.strip():
        return None
    digits = re.sub(r'\D', '', phone)
    if len(digits) not in (PHONE_DIGITS_LENGTH_1, PHONE_DIGITS_LENGTH_2):
        raise forms.ValidationError(
            f'Номер телефона должен содержать {PHONE_DIGITS_LENGTH_1} или '
            f'{PHONE_DIGITS_LENGTH_2} цифр'
        )
    if (
        len(digits) == PHONE_DIGITS_LENGTH_2
        and digits.startswith(PHONE_START_DIGIT)
    ):
        digits = PHONE_REPLACE_DIGIT + digits[1:]
    elif len(digits) == PHONE_DIGITS_LENGTH_1:
        digits = PHONE_REPLACE_DIGIT + digits
    normalized_phone = '+' + digits
    user_query = User.objects.filter(phone=normalized_phone)
    if instance and instance.pk:
        user_query = user_query.exclude(pk=instance.pk)
    if user_query.exists():
        raise forms.ValidationError(
            'Пользователь с таким номером телефона уже существует'
        )
    return normalized_phone


def validate_github_url(url):
    """Валидация корректности GitHub URL."""
    if not url:
        return url

    if 'github.com' not in url.lower():
        raise forms.ValidationError('Ссылка должна вести на GitHub')

    return url


def generate_avatar_image(user_obj):
    """Создание аватарки на основе имени пользователя"""

    raw_name = getattr(user_obj, 'name', None) or ''
    letter = (raw_name.strip() or 'U')[0].upper()

    if user_obj.pk:
        seed = user_obj.pk
    else:
        hash_bytes = hashlib.blake2b(
            (user_obj.email or 'user').encode('utf-8'),
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
    email_slug = user_obj.email.split('@')[0] if user_obj.email else 'user'
    filename = f'avatar_{email_slug}_{letter}.png'
    return ContentFile(buffer.getvalue(), name=filename)


def paginate_queryset(request, queryset, items_per_page=12):
    """Универсальная функция пагинации"""

    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
