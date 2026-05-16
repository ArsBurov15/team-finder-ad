from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def redirect_to_projects(request):
    return redirect('projects:list', permanent=False)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_projects, name='root'),
    path('users/', include('users.urls')),
    path('projects/', include('projects.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
