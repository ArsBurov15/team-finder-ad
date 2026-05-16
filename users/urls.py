from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.sign_up_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.sign_out_view, name='logout'),
    path('profile/<int:pk>/', views.user_profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='profile_edit'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    path('list/', views.user_list_view, name='user_list'),
]