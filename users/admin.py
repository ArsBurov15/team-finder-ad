from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

UserModel = get_user_model()


@admin.register(UserModel)
class CustomUserAdmin(BaseUserAdmin):
    """Управление пользователями"""

    list_display = ('id', 'email', 'name', 'surname', 'is_active')
    list_display_links = ('email',)
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'phone')
    ordering = ('email',)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                ('Новый аккаунт', {
                    'fields': ('email', 'password', 'name', 'surname')
                }),
            )

        return (
            ('Главное', {
                'fields': ('email', 'password', 'is_active', 'is_staff')
            }),
            ('Данные', {
                'fields': (
                    'name',
                    'surname',
                    'phone',
                    'avatar',
                    'github_url',
                    'about',
                )
            }),
            ('Избранное', {
                'fields': ('favorites',)
            }),
        )