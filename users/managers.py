from django.contrib.auth.models import BaseUserManager


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
