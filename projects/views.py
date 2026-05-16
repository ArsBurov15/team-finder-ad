from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .constants import PROJECTS_PER_PAGE
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm
from django.views.decorators.http import require_POST


def project_list_view(request):
    """Список всех проектов"""

    projects_queryset = (
        Project.objects
        .select_related('owner')
        .prefetch_related('participants')
        .order_by('-created_at', '-id')
    )
    project_paginator = Paginator(projects_queryset, PROJECTS_PER_PAGE)
    current_page = request.GET.get('page')
    paginated_page = project_paginator.get_page(current_page)
    view_context = {
        'page_obj': paginated_page,
    }
    return render(request, 'projects/project_list.html', view_context)


@login_required
def favorite_projects_view(request):
    """Страница избранных проектов"""

    current_user = request.user
    favorite_queryset = (
        current_user.favorites
        .select_related('owner')
        .prefetch_related('participants')
        .order_by('-created_at', '-id')
    )
    favorite_paginator = Paginator(favorite_queryset, PROJECTS_PER_PAGE)
    current_page = request.GET.get('page')
    paginated_page = favorite_paginator.get_page(current_page)

    view_context = {
        'projects': paginated_page,
    }
    return render(request, 'projects/favorite_projects.html', view_context)


def project_detail_view(request, pk):
    """Детальная информация о проекте"""

    project_instance = get_object_or_404(
        Project.objects.select_related(
            'owner').prefetch_related('participants'),
        pk=pk
    )
    is_participant = False
    is_owner = False
    is_favorited = False
    current_user = request.user
    if current_user.is_authenticated:
        is_participant = current_user in project_instance.participants.all()
        is_owner = project_instance.owner == current_user
        is_favorited = current_user.favorites.filter(
            pk=project_instance.pk).exists()
    view_context = {
        'project': project_instance,
        'is_participant': is_participant,
        'is_owner': is_owner,
        'is_favorited': is_favorited,
    }
    return render(request, 'projects/project-details.html', view_context)


@login_required
def project_create_view(request):
    """Создание нового проекта"""

    current_user = request.user
    if request.method != 'POST':
        empty_form = ProjectForm()
        return render(
            request,
            'projects/create-project.html',
            {'form': empty_form, 'is_edit': False}
        )
    filled_form = ProjectForm(request.POST)

    if filled_form.is_valid():
        new_project = filled_form.save(commit=False)
        new_project.owner = current_user
        new_project.save()
        new_project.participants.add(current_user)
        return redirect('projects:detail', pk=new_project.pk)
    return render(
        request,
        'projects/create-project.html',
        {'form': filled_form, 'is_edit': False}
    )


@login_required
def project_edit_view(request, pk):
    """Редактирование проекта"""

    current_user = request.user
    existing_project = get_object_or_404(Project, pk=pk)
    if existing_project.owner != current_user:
        raise PermissionDenied("Вы не можете редактировать этот проект")
    if request.method != 'POST':
        edit_form = ProjectForm(instance=existing_project)
        return render(request, 'projects/create-project.html', {
            'form': edit_form,
            'is_edit': True
        })
    filled_form = ProjectForm(request.POST, instance=existing_project)
    if filled_form.is_valid():
        updated_project = filled_form.save()
        return redirect('projects:detail', pk=updated_project.pk)
    return render(request, 'projects/create-project.html', {
        'form': filled_form,
        'is_edit': True
    })


@login_required
@require_POST
def toggle_favorite_view(request, pk):
    """Добавить/удалить проект из избранного"""

    user_profile = request.user
    project_obj = get_object_or_404(Project, pk=pk)
    is_already_favorited = user_profile.favorites.filter(
        id=project_obj.id).exists()
    if is_already_favorited:
        user_profile.favorites.remove(project_obj)
        is_now_favorited = False
    else:
        user_profile.favorites.add(project_obj)
        is_now_favorited = True
    return JsonResponse({
        'status': 'ok',
        'favorited': is_now_favorited
    })


@login_required
@require_POST
def close_project_view(request, pk):
    """Завершить проект"""
    current_user = request.user
    target_project = get_object_or_404(Project, pk=pk)

    if target_project.owner != current_user:
        error_response = {
            'status': 'error',
            'message': 'У вас нет прав на это действие',
        }
        return JsonResponse(error_response, status=403)

    if target_project.status != target_project.STATUS_OPEN:
        error_response = {
            'status': 'error',
            'message': 'Проект уже завершён',
        }
        return JsonResponse(error_response, status=400)

    target_project.status = target_project.STATUS_CLOSED
    target_project.save(update_fields=['status'])

    return JsonResponse({
        'status': 'ok',
        'project_status': target_project.STATUS_CLOSED,
    })


@login_required
@require_POST
def toggle_participate_view(request, pk):
    """Участие/выход из проекта"""

    current_user = request.user
    target_project = get_object_or_404(Project, pk=pk)
    if target_project.owner == current_user:
        return JsonResponse({
            'status': 'error',
            'message': 'Организатор не может покинуть собственный проект'
        }, status=400)
    is_participating = current_user.participated_projects.filter(
        id=target_project.id).exists()
    if is_participating:
        current_user.participated_projects.remove(target_project)
        is_now_participating = False
    else:
        current_user.participated_projects.add(target_project)
        is_now_participating = True
    return JsonResponse({
        'status': 'ok',
        'is_participant': is_now_participating
    })
