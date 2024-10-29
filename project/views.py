from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from project.models import RawRequest, Project
from project.forms import ProjectInitialForm

from SEP.models import Customer

# Create your views here.
@login_required
def create_project_from_raw(request, id: int):
    raw_request = get_object_or_404(RawRequest, id=id)

    try:
        project = raw_request.project
    except RawRequest.project.RelatedObjectDoesNotExist:
        project = None

    if request.method == "POST":
        project_form = ProjectInitialForm(request.POST, instance=project)

        if project_form.is_valid():
            # Do not commit to avoid IntegrityError
            project = project_form.save(commit=False)
            project.created_by = request.user

            if project.initial_request is None:
                project.initial_request = raw_request

            if "save_draft" in request.POST:
                project.status = "draft"
                messages.success(request, "Draft saved !")
            elif "publish_project" in request.POST:
                project.status = "pending"
                messages.success(request, "Project sent to the CS manager !")
            project.save()

            return HttpResponseRedirect(reverse("employee_home"))
        else:
            messages.error(request, "Please correct the errors below.")

    # Get data from existing draft project if it exists
    if project is not None:
        if project.status != "draft":
            messages.error(request, "You cannot modify this request anymore.")
            return HttpResponseRedirect(reverse("employee_home"))

        project_form = ProjectInitialForm(instance=project)
    else:
        project_form = ProjectInitialForm(initial={
            "estimated_budget": raw_request.available,
            "client": Customer.objects.get_or_create(
                name=raw_request.name,
                email=raw_request.email,
                phone=raw_request.phone,
                address=raw_request.address,
            )[0],
        })

    context = {
        "raw_request": raw_request,
        "project_form": project_form,
    }

    return render(request, "raw_request.html", context=context)


@login_required
def project_detail(request, project_id: int):
    project = get_object_or_404(Project, id=project_id)

    context = {
        "project": project,
    }

    return render(request, "project_detail.html", context=context)
