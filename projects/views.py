import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import ProjectForm
from .models import Project, Skill


def _project_queryset():
    projects = Project.objects.all()
    projects = projects.order_by("-created_at")
    return projects


def project_list(request):
    active_skill = request.GET.get("skill")
    projects = _project_queryset()
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    paginator = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    all_skills = Skill.objects.values_list("name", flat=True)
    all_skills = all_skills.order_by("name")

    context = {
        "projects": page_obj.object_list,
        "page_obj": page_obj,
        "all_skills": all_skills,
        "active_skill": active_skill,
    }
    return render(request, "projects/project_list.html", context)


def project_detail(request, project_id):
    project = get_object_or_404(_project_queryset(), pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("Редактировать проект может только автор")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return JsonResponse({"status": "forbidden"}, status=403)
    if project.status == Project.STATUS_OPEN:
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "ok", "participant": True})

    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@require_GET
def skill_suggestions(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.all()

    if query:
        skills = skills.filter(name__istartswith=query)

    skills = skills.order_by("name")
    skills = skills.values("id", "name")[:10]
    data = list(skills)
    return JsonResponse(data, safe=False)


def _payload(request):
    if request.content_type == "application/json":
        try:
            if request.body:
                return json.loads(request.body)
            return {}
        except json.JSONDecodeError:
            return {}
    return request.POST


@login_required
@require_POST
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return JsonResponse({"status": "forbidden"}, status=403)

    payload = _payload(request)
    skill_id = payload.get("skill_id")
    name = payload.get("name")
    if name:
        name = name.strip()
    else:
        name = ""

    created = False
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(
            name__iexact=name,
            defaults={"name": name},
        )
    else:
        return JsonResponse({"error": "skill_id or name is required"}, status=400)

    already_added = project.skills.filter(pk=skill.pk).exists()
    if not already_added:
        project.skills.add(skill)

    answer = {
        "id": skill.id,
        "name": skill.name,
        "skill_id": skill.id,
        "created": created,
        "added": not already_added,
    }
    return JsonResponse(answer)


@login_required
@require_POST
def remove_skill(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return JsonResponse({"status": "forbidden"}, status=403)
    skill = get_object_or_404(Skill, pk=skill_id)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok", "removed": True})
