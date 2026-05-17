from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Управление проектами"""

    list_display = ('name', 'owner', 'status', 'created_at')
    list_display_links = ('name',)
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'owner__email', 'owner__name')
    raw_id_fields = ('owner',)
    filter_horizontal = ('participants',)

    def get_fieldsets(self, request, obj=None):
        base_fields = ('name', 'description', 'owner', 'status')
        if obj is None:
            return (
                ('Новый проект', {'fields': base_fields}),
            )
        return (
            ('Основная информация', {'fields': base_fields}),
            ('Команда и ссылки', {
                'fields': ('github_url', 'participants')
            }),
            ('Служебная информация', {
                'fields': ('created_at',)
            }),
        )

    def get_add_fieldsets(self, request):
        return self.get_fieldsets(request, obj=None)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('created_at',)
        return ()
