from django import forms

from projects.models import Project


class ProjectForm(forms.ModelForm):
    """Форма для проекта"""

    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'status')
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
            'github_url': 'Ссылка на GitHub',
            'status': 'Статус',
        }
        widgets = {
            "name": forms.TextInput(attrs={'placeholder': 'Введите название'}),
            "description": forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Опишите проект'
            }),
        }

    def clean_github_url(self):
        """Валидация GitHub URL"""
        url = self.cleaned_data.get('github_url')

        if not url:
            return url

        url = url.strip()

        if 'github.com' not in url.lower():
            raise forms.ValidationError(
                'Ссылка должна вести на GitHub (github.com)')

        return url
