from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.constants import PROJECTS_PER_PAGE
from projects.forms import ProjectForm
from projects.models import Project


def paginate_projects(request, queryset):
    """Функция пагинации"""

    paginator = Paginator(queryset, PROJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def project_list_view(request):
    """Список всех проектов"""
    projects_queryset = (
        Project.objects
        .select_related('owner')
        .prefetch_related('participants')
        .order_by('-created_at', '-id')
    )
    page_obj = paginate_projects(request, projects_queryset)

    return render(
        request,
        'projects/project_list.html',
        {'page_obj': page_obj}
    )


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
    page_obj = paginate_projects(request, favorite_queryset)

    return render(
        request,
        'projects/favorite_projects.html',
        {'projects': page_obj}
    )


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
        is_participant = project_instance.participants.filter(
            pk=current_user.pk
        ).exists()
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
    project_obj = Project.objects.filter(pk=pk).first()
    if project_obj is None:
        return JsonResponse(
            {'status': 'error', 'message': 'Проект не найден'},
            status=HTTPStatus.NOT_FOUND
        )
    is_favorited = user_profile.favorites.filter(id=project_obj.id).exists()
    if is_favorited:
        user_profile.favorites.remove(project_obj)
    else:
        user_profile.favorites.add(project_obj)
    return JsonResponse({
        'status': 'ok',
        'favorited': not is_favorited
    })


@login_required
@require_POST
def close_project_view(request, pk):
    """Завершить проект"""

    current_user = request.user
    target_project = Project.objects.filter(pk=pk).first()

    if target_project is None:
        return JsonResponse(
            {'status': 'error', 'message': 'Проект не найден'},
            status=HTTPStatus.NOT_FOUND
        )
    if target_project.owner != current_user:
        error_response = {
            'status': 'error',
            'message': 'У вас нет прав на это действие',
        }
        return JsonResponse(error_response, status=HTTPStatus.FORBIDDEN)
    if target_project.status != target_project.STATUS_OPEN:
        error_response = {
            'status': 'error',
            'message': 'Проект уже завершён',
        }
        return JsonResponse(error_response, status=HTTPStatus.BAD_REQUEST)
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
    target_project = Project.objects.filter(pk=pk).first()
    if target_project is None:
        return JsonResponse(
            {'status': 'error', 'message': 'Проект не найден'},
            status=HTTPStatus.NOT_FOUND
        )
    if target_project.status != target_project.STATUS_OPEN:
        return JsonResponse({
            'status': 'error',
            'message': 'Нельзя участвовать в закрытом проекте'
        }, status=HTTPStatus.BAD_REQUEST)
    if target_project.owner == current_user:
        return JsonResponse({
            'status': 'error',
            'message': 'Организатор не может покинуть собственный проект'
        }, status=HTTPStatus.BAD_REQUEST)
    is_participating = current_user.participated_projects.filter(
        id=target_project.id
    ).exists()
    if is_participating:
        current_user.participated_projects.remove(target_project)
    else:
        current_user.participated_projects.add(target_project)
    return JsonResponse({
        'status': 'ok',
        'participant': not is_participating
    })
