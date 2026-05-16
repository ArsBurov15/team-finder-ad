import re
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .constants import (
    NAME_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ABOUT_MAX_LENGTH
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
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UpdatePasswordForm(forms.Form):
    """Форма смены пароля"""

    current_password = forms.CharField(
        label="Действующий пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите старый пароль'})
    )
    password_prime = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Минимум 8 символов'})
    )
    password_repeat = forms.CharField(
        label="Повтор нового пароля",
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите еще раз'})
    )
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Неверный действующий пароль')
        return current_password
    
    def clean_password_prime(self):
        password = self.cleaned_data.get('password_prime')
        if password and len(password) < 8:
            raise forms.ValidationError('Пароль должен содержать минимум 8 символов')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password_prime = cleaned_data.get('password_prime')
        password_repeat = cleaned_data.get('password_repeat')
        
        if password_prime and password_repeat and password_prime != password_repeat:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data
    
    def save(self):
        new_password = self.cleaned_data.get('password_prime')
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
        widget=forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX или 8XXXXXXXXXX'})
    )
    
    github_url = forms.URLField(
        required=False,
        label="Профиль GitHub",
        widget=forms.URLInput(attrs={'placeholder': 'https://github.com/username'})
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
            'name': forms.TextInput(attrs={'placeholder': 'Введите имя'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Введите фамилию'}),
            'avatar': forms.FileInput(),
            'about': forms.Textarea(attrs={'placeholder': 'Расскажите о себе', 'rows': 4}),
        }

    def clean_phone(self):
        """Валидация номера телефона."""
        phone = self.cleaned_data.get('phone')
        
        if not phone:
            return phone
        digits = re.sub(r'\D', '', phone)
        if len(digits) not in (10, 11):
            raise forms.ValidationError('Номер телефона должен содержать 10 или 11 цифр')
        if len(digits) == 11 and digits.startswith('8'):
            digits = '7' + digits[1:]
        elif len(digits) == 10:
            digits = '7' + digits
        normalized_phone = '+' + digits
        user_query = User.objects.filter(phone=normalized_phone)
        if self.instance and self.instance.pk:
            user_query = user_query.exclude(pk=self.instance.pk)
            
        if user_query.exists():
            raise forms.ValidationError('Пользователь с таким номером телефона уже существует')

        return normalized_phone

    def clean_github_url(self):
        """Валидация корректности GitHub URL."""
        url = self.cleaned_data.get('github_url')

        if not url:
            return url

        if 'github.com' not in url.lower():
            raise forms.ValidationError('Ссылка должна вести на GitHub')

        return url