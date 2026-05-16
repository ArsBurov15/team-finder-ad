from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_test_users(apps, schema_editor):
    """Создание тестовых пользователей"""
    User = apps.get_model('users', 'User')

    default_password = make_password('testpass123')

    users_data = [
        {
            'email': 'user1@example.com',
            'name': 'Иван',
            'surname': 'Иванов',
            'phone': '+79123456789',
            'password': default_password,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'email': 'user2@example.com',
            'name': 'Пётр',
            'surname': 'Петров',
            'phone': '+79234567890',
            'password': default_password,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'email': 'maria@yandex.ru',
            'name': 'Мария',
            'surname': 'Сидорова',
            'phone': '+79345678901',
            'password': default_password,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'email': 'admin@example.com',
            'name': 'Admin',
            'surname': 'Adminov',
            'phone': '+79999999999',
            'password': default_password,
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        },
    ]

    for user_data in users_data:
        if not User.objects.filter(email=user_data['email']).exists():
            User.objects.create(**user_data)


def reverse_func(apps, schema_editor):
    """Откат: удаляем тестовых пользователей"""
    User = apps.get_model('users', 'User')
    emails = [
        'admin@example.com',
        'user1@example.com',
        'user2@example.com',
        'maria@yandex.ru',
    ]
    User.objects.filter(email__in=emails).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_alter_user_phone'),
    ]

    operations = [
        migrations.RunPython(create_test_users, reverse_func),
    ]
