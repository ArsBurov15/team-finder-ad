from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm, ProfileEditorForm, UpdatePasswordForm
from .constants import FILTER_BUTTONS
from projects.models import Project

User = get_user_model()

def sign_up_view(request):
    """Регистрация пользователя"""
    
    registration_form = RegistrationForm(data=request.POST or None)
    
    if not registration_form.is_valid():
        return render(request, 'users/register.html', {'form': registration_form})
    
    created_user = registration_form.save()
    login(request, created_user)
    
    return redirect('projects:list')


def login_view(request):
    """Аутентификация пользователя"""
    
    login_form = LoginForm(request=request, data=request.POST or None)
    
    if not login_form.is_valid():
        return render(request, 'users/login.html', {'form': login_form})
    
    authenticated_user = login_form.get_user()
    login(request, authenticated_user)
    
    return redirect('projects:list')

def sign_out_view(request):
    """Выход пользователя из системы"""
    
    logout(request)
    return redirect('projects:list')

def user_profile_view(request, pk):
    """Страница пользователя: профиль и проекты пользователя"""
    
    profile_owner = get_object_or_404(User, pk=pk)
    user_projects = Project.objects.filter(owner=profile_owner).select_related('owner').order_by('-created_at')
    context = {
        'profile_owner': profile_owner,
        'user_projects': user_projects,
    }
    
    return render(request, 'users/user-details.html', context)

@login_required
def edit_profile_view(request):
    """Редактирование профиля (только для владельца)"""
    
    current_user = request.user
    if request.method != 'POST':
        blank_form = ProfileEditorForm(instance=current_user)
        return render(request, 'users/edit_profile.html', {'form': blank_form})
    
    filled_form = ProfileEditorForm(request.POST, request.FILES, instance=current_user)
    
    if filled_form.is_valid():
        filled_form.save()
        return redirect('users:profile', pk=current_user.pk)
    
    return render(request, 'users/edit_profile.html', {'form': filled_form})

def user_list_view(request):
    """Список пользователей с пагинацией"""
    
    all_users = User.objects.all().order_by('-date_joined')
    selected_filter = request.GET.get('filter')
    
    if not (request.user.is_authenticated and selected_filter):
        paginator = Paginator(all_users, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'participants': page_obj,
            'active_filter': '',
            'filter_options': FILTER_BUTTONS,
        }
        return render(request, 'users/participants.html', context)
    
    filtered_users = all_users
    
    if selected_filter == 'authors_of_favorite_projects':
        filtered_users = filtered_users.filter(owned_projects__interested_users=request.user)
    
    elif selected_filter == 'authors_of_my_participated_projects':
        filtered_users = filtered_users.filter(owned_projects__participants=request.user)
    
    elif selected_filter == 'users_who_like_my_projects':
        filtered_users = filtered_users.filter(favorites__owner=request.user)
    
    elif selected_filter == 'participants_of_my_projects':
        filtered_users = filtered_users.filter(participated_projects__owner=request.user)
    
    filtered_users = filtered_users.exclude(pk=request.user.pk).distinct()
    
    paginator = Paginator(filtered_users, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'participants': page_obj,
        'active_filter': selected_filter,
        'filter_options': FILTER_BUTTONS,
    }
    
    return render(request, 'users/participants.html', context)

@login_required
def change_password_view(request):
    """Смена пароля (только для авторизованных пользователей)"""
    
    current_user = request.user
    if request.method != 'POST':
        empty_form = UpdatePasswordForm(user=current_user)
        return render(request, 'users/change_password.html', {'form': empty_form})
    
    submitted_form = UpdatePasswordForm(request.POST, user=current_user)
    
    if submitted_form.is_valid():
        updated_user = submitted_form.save()
        update_session_auth_hash(request, updated_user)
        
        return redirect('users:profile', pk=current_user.pk)
    
    return render(request, 'users/change_password.html', {'form': submitted_form})