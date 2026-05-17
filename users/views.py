from django.contrib.auth import (
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from users.constants import (
    FILTER_AUTHORS_OF_FAVORITE,
    FILTER_AUTHORS_OF_PARTICIPATING,
    FILTER_INTERESTED_IN_MY,
    FILTER_PARTICIPANTS_OF_MY,
    FILTER_BUTTONS,
    USERS_PER_PAGE,
)
from users.forms import (
    LoginForm,
    ProfileEditorForm,
    RegistrationForm,
    UpdatePasswordForm,
)

User = get_user_model()


def paginate_users(request, queryset):
    """Функция пагинации для пользователей"""

    paginator = Paginator(queryset, USERS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def sign_up_view(request):
    """Регистрация пользователя"""

    registration_form = RegistrationForm(data=request.POST or None)

    if not registration_form.is_valid():
        return render(
            request,
            'users/register.html',
            {'form': registration_form}
        )

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
    user_projects = profile_owner.owned_projects.all()
    user_projects = user_projects.select_related('owner')
    user_projects = user_projects.order_by('-created_at')

    context = {
        'user': profile_owner,
        'user_projects': user_projects,
    }

    return render(request, 'users/user-details.html', context)


@login_required
def edit_profile_view(request):
    """Редактирование профиля"""

    current_user = request.user

    if request.method != 'POST':
        blank_form = ProfileEditorForm(instance=current_user)
        return render(
            request,
            'users/edit_profile.html',
            {'form': blank_form}
        )

    filled_form = ProfileEditorForm(
        request.POST,
        request.FILES,
        instance=current_user
    )

    if filled_form.is_valid():
        filled_form.save()
        return redirect('users:profile', pk=current_user.pk)

    return render(
        request,
        'users/edit_profile.html',
        {'form': filled_form}
    )


def user_list_view(request):
    """Список пользователей"""

    all_users = User.objects.all().order_by('-date_joined')
    selected_filter = request.GET.get('filter')

    if not (request.user.is_authenticated and selected_filter):
        page_obj = paginate_users(request, all_users)
        context = {
            'page_obj': page_obj,
            'active_filter': '',
            'filter_options': FILTER_BUTTONS,
        }
        return render(request, 'users/participants.html', context)

    filtered_users = all_users

    if selected_filter == FILTER_AUTHORS_OF_FAVORITE:
        filtered_users = filtered_users.filter(
            owned_projects__interested_users=request.user
        )
    elif selected_filter == FILTER_AUTHORS_OF_PARTICIPATING:
        filtered_users = filtered_users.filter(
            owned_projects__participants=request.user
        )
    elif selected_filter == FILTER_INTERESTED_IN_MY:
        filtered_users = filtered_users.filter(
            favorites__owner=request.user
        )
    elif selected_filter == FILTER_PARTICIPANTS_OF_MY:
        filtered_users = filtered_users.filter(
            participated_projects__owner=request.user
        )

    filtered_users = filtered_users.exclude(pk=request.user.pk).distinct()

    page_obj = paginate_users(request, filtered_users)
    context = {
        'page_obj': page_obj,
        'active_filter': selected_filter,
        'filter_options': FILTER_BUTTONS,
    }
    return render(request, 'users/participants.html', context)


@login_required
def change_password_view(request):
    """Смена пароля"""

    current_user = request.user

    if request.method != 'POST':
        empty_form = UpdatePasswordForm(user=current_user)
        return render(
            request,
            'users/change_password.html',
            {'form': empty_form}
        )
    submitted_form = UpdatePasswordForm(
        user=current_user,
        data=request.POST
    )

    if submitted_form.is_valid():
        updated_user = submitted_form.save()
        update_session_auth_hash(request, updated_user)
        return redirect('users:profile', pk=current_user.pk)

    return render(
        request,
        'users/change_password.html',
        {'form': submitted_form}
    )
