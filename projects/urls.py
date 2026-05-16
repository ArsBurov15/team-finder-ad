from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.project_list_view, name='list'),
    path('favorites/', views.favorite_projects_view, name='favorites'),
    path('create-project/', views.project_create_view, name='create'),
    path('<int:pk>/edit/', views.project_edit_view, name='edit'),
    path('<int:pk>/', views.project_detail_view, name='detail'),
    path('<int:pk>/toggle-favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('<int:pk>/close/', views.close_project_view, name='close'),
    path('<int:pk>/toggle-participate/', views.toggle_participate_view, name='toggle_participate'),
]