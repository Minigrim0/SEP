from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from project.models import RawRequest, Project
from project.forms import ProjectInitialForm

# Create your views here.
@login_required
def create_project_from_raw(request, id: int):
    raw_request = get_object_or_404(RawRequest, id=id)

    # Get data from existing draft project if it exists
    try:
        if raw_request.project.status != "DRAFT":
            messages.error(request, "You cannot modify this request anymore.")
            return HttpResponseRedirect(reverse("project:employee_home"))

        project_form = ProjectInitialForm(instance=project.ref_project)
    except RawRequest.project.RelatedObjectDoesNotExist:
        project_form = ProjectInitialForm(initial={"estimated_budget": raw_request.available})

    context = {
        "raw_request": raw_request,
        "project_form": project_form,
    }

    return render(request, "raw_request.html", context=context)
