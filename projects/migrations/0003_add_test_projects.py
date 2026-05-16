from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_test_projects(apps, schema_editor):
    """Создание тестовых проектов"""
    User = apps.get_model('users', 'User')
    Project = apps.get_model('projects', 'Project')

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
    ]

    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        created_users.append(user)

    try:
        user1 = User.objects.get(email='user1@example.com')
        user2 = User.objects.get(email='user2@example.com')
    except User.DoesNotExist:
        return

    projects_data = [
        {
            'name': 'TeamFinder Platform',
            'description': 'Платформа для поиска команды над pet-проектами',
            'owner': user1,
            'github_url': 'https://github.com/example/teamfinder',
            'status': 'open',
        },
        {
            'name': 'Docker App',
            'description': 'Веб-приложение с Docker Compose',
            'owner': user2,
            'status': 'open',
        },
        {
            'name': 'Завершённый проект',
            'description': 'Пример закрытого проекта',
            'owner': user1,
            'status': 'closed',
        },
    ]

    for project_data in projects_data:
        project, created = Project.objects.get_or_create(
            name=project_data['name'],
            defaults=project_data
        )
        if created:
            project.participants.add(project.owner)
            print(f'Создан проект: {project.name}')
        else:
            print(f'Проект уже существует: {project.name}')


def reverse_func(apps, schema_editor):
    """Откат: удаляем тестовые проекты и пользователей"""
    User = apps.get_model('users', 'User')
    Project = apps.get_model('projects', 'Project')

    Project.objects.filter(name__in=[
        'TeamFinder Platform',
        'Docker App',
        'Завершённый проект',
    ]).delete()

    User.objects.filter(email__in=[
        'user1@example.com',
        'user2@example.com',
        'maria@yandex.ru',
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0002_initial'),
        ('users', '0003_alter_user_phone'),
    ]

    operations = [
        migrations.RunPython(create_test_projects, reverse_func),
    ]
