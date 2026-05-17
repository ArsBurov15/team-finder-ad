from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

from users.constants import PHONE_MAX_LENGTH, PASSWORD_MIN_LENGTH
from users.utils import (
    generate_avatar_image,
    validate_github_url,
    validate_phone,
)


User = get_user_model()


class RegistrationForm(forms.ModelForm):
    """"Форма регистрации"""

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            if not user.avatar:
                avatar_file = generate_avatar_image(user)
                user.avatar.save(avatar_file.name, avatar_file, save=True)

        return user


class UpdatePasswordForm(forms.Form):
    """Форма смены пароля"""

    old_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Введите старый пароль'})
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Минимум 8 символов'})
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите еще раз'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Неверный действующий пароль')
        return old_password

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password and len(password) < PASSWORD_MIN_LENGTH:
            raise forms.ValidationError(
                f'Пароль должен содержать '
                f'минимум {PASSWORD_MIN_LENGTH} символов'
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data

    def save(self):
        new_password = self.cleaned_data.get('new_password1')
        self.user.set_password(new_password)
        self.user.save()
        return self.user


class LoginForm(forms.Form):
    """Форма входа"""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Введите email'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not (email and password):
            return cleaned_data

        account = User.objects.filter(email=email).first()

        if account is None:
            raise ValidationError('Неверный email или пароль')

        self.user = authenticate(
            request=self.request,
            username=account.email,
            password=password
        )

        if self.user is None:
            raise ValidationError('Неверный email или пароль')

        if not self.user.is_active:
            raise ValidationError('Учётная запись не активна')

        return cleaned_data

    def get_user(self):
        return self.user


class ProfileEditorForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=PHONE_MAX_LENGTH,
        label="Контактный телефон",
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': '+7XXXXXXXXXX или 8XXXXXXXXXX'})
    )

    github_url = forms.URLField(
        required=False,
        label="Профиль GitHub",
        widget=forms.URLInput(
            attrs={'placeholder': 'https://github.com/username'})
    )

    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'about', 'phone', 'github_url')
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'avatar': 'Аватар',
            'about': 'О себе',
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Введите имя'}
            ),
            'surname': forms.TextInput(
                attrs={'placeholder': 'Введите фамилию'}
            ),
            'avatar': forms.FileInput(),
            'about': forms.Textarea(
                attrs={'placeholder': 'Расскажите о себе', 'rows': 4}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return validate_phone(phone, instance=self.instance)

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        return validate_github_url(url)
