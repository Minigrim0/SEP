from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from project.models import RawRequest, Project
from project.forms import ProjectInitialForm, FinancialFeedbackForm, TaskAssignmentForm

from SEP.models import Customer, Team


@login_required
def create_project_from_raw(request, id: int):
    """Allows a CS employee to create a new project based on a raw request."""

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

            # Either save the project as a draft or send it to the CS manager
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
    elif project is not None:  # Get initial data from existing project
        if project.status != "draft":
            messages.error(request, "You cannot modify this request anymore.")
            return HttpResponseRedirect(reverse("employee_home"))

        project_form = ProjectInitialForm(instance=project)
    else:  # Create a new empty form that will create a new project once submitted
        project_form = ProjectInitialForm(initial={
            "estimated_budget": raw_request.available,  # Set the estimated budget to the available budget to avoid a step for the cs employee
            "client": Customer.objects.get_or_create(  # try to find the customer, create it if it doesn't exist
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
def project_list(request):
    projects = Project.objects.all().order_by("created_at")
    return render(request, "project_list.html", context={"projects": projects})

@login_required
def project_detail(request, project_id: int):
    """Displays the details of a project.

        TODO: Add actions to the page depending on the user's role and the project's status.
    """

    project = get_object_or_404(Project, id=project_id)
    return render(request, "project_detail.html", context={"project": project})


@login_required
def csm_action(request, project_id: int):
    """Allows the CSM to approve or reject a project"""

    project = get_object_or_404(Project, id=project_id)
    action = request.GET.get("approve", None)

    if action is None:
        messages.error(request, "Invalid action.")
        # Redirect to the previous page or to the employee's home page
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("employee_home")))

    if action == "1":
        # Approve the project, push it to the next step.
        project.status = "cs_approved"
        project.save()
        messages.success(request, "Project approved !")
    else:
        # Reject the project
        project.status = "cs_rejected"
        project.save()
        messages.success(request, "Project rejected !")

    return HttpResponseRedirect(reverse("employee_home"))


@login_required
def fin_action(request, project_id: int):
    """Allows the finance manager to write feedback on the project before sending it to the administration manager"""

    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = FinancialFeedbackForm(request.POST)
        if form.is_valid():
            project.financial_feedback = form.cleaned_data.get("feedback", None)

            if "save_draft" in request.POST:
                # Just save the project as a draft
                messages.success(request, "The feedback draft has been saved.")
                project.financial_feedback_draft_status = True  # This is for visual porposes only
            else:
                # Save the feedback and forward the project to the administration manager
                messages.success(request, "The feedback has been saved and sent to the administration departmenent.")
                project.financial_feedback_draft_status = False
                project.status = "fin_review"

            project.save()
            return HttpResponseRedirect(reverse("employee_home"))
        else:
            messages.error(request, "Please correct the error(s) below")

    else:
        form = FinancialFeedbackForm(initial={"feedback": project.financial_feedback})

    return render(request, "financial_feedback.html", context={"feedback_form": form, "project": project})


@login_required
def adm_action(request, project_id: int):
    """Allows the ADM to approve or reject a project"""

    project = get_object_or_404(Project, id=project_id)
    action = request.GET.get("approve", None)

    if action is None:
        messages.error(request, "Invalid action.")
        # Redirect to the previous page or to the employee's home page
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("employee_home")))

    if action == "1":
        # Approve the project, push it to the next step.
        project.status = "admin_approved"
        project.save()
        messages.success(request, "Project approved !")
    else:
        # Reject the project
        project.status = "admin_rejected"
        project.save()
        messages.success(request, "Project rejected !")

    return HttpResponseRedirect(reverse("employee_home"))


@login_required
def psdm_action(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    context = {}
    context["project"] = project
    context["teams"] = Team.objects.filter(manager=request.user)
    context["dept"] = "Services" if request.user.role.id == "SDM" else "Production"

    return render(request, "psdm_project_view.html", context=context)


@login_required
def psdm_team_action(request, project_id, team_id):
    project = get_object_or_404(Project, id=project_id)
    team = get_object_or_404(Team, id=team_id)

    if request.method == "POST":
        form = TaskAssignmentForm(request.POST, team=team)

        if form.is_valid():
            task = form.save(commit=False)
            task.sender = request.user
            task.project = project
            task.save()

            messages.success(request, "Task assigned successfully.")
            return HttpResponseRedirect(reverse("project:psdm_action", args=[project_id]))
        else:
            messages.error(request, "Please correct the error(s) below.")

    else:
        form = TaskAssignmentForm(team=team)

    context = {
        "project": project,
        "team": team,
        "form": form,
    }

    return render(request, "psdm_task_create.html", context=context)
