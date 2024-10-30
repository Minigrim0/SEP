from django.core.handlers.asgi import HttpResponseBadRequest
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from project.forms import RawRequestForm
from project.models import FinancialRequest, RawRequest, Project, Task, RecruitementPost


def home(request):
    """Home page for the customers."""

    if request.method == "POST":
        request_form = RawRequestForm(request.POST)

        if request_form.is_valid():
            messages.success(request, "Request submitted successfully.")
            request_form.save()
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        request_form = RawRequestForm()

    return render(request, "index.html", context={"form": request_form})


@login_required
def employee_home(request):
    """Home page for the employees."""

    context = {}

    if request.user.role.id == "CSE":
        context["raw_requests"] = RawRequest.objects.filter(Q(project=None) | Q(project__status="draft"))
        context["project_history"] = Project.objects.filter(created_by=request.user).exclude(status="draft").order_by("-created_at")[:25]

        return render(request, "employee/CSE.html", context=context)
    elif request.user.role.id == "CSM":
        context["waiting_approval"] = Project.objects.filter(status="pending")
        context["project_history"] = Project.objects.exclude(status="draft").exclude(status="pending").order_by("-created_at")[:25]

        return render(request, "employee/CSM.html", context=context)
    elif request.user.role.id == "FIM":

        if request.method == "POST":
            fin_request_id = request.POST.get("fin_request_id")
            fin_request = get_object_or_404(FinancialRequest, id=fin_request_id)

            if "approve_fin" in request.POST:
                fin_request.status = "approved"
                messages.success(request, "Financial request approved.")
            elif "reject_fin" in request.POST:
                fin_request.status = "rejected"
                messages.success(request, "Financial request rejected.")
            else:
                return HttpResponseBadRequest("Invalid action.")
            fin_request.save()

        context["waiting_feedback"] = Project.objects.filter(status="cs_approved")
        context["project_history"] = Project.objects.filter(Q(status="admin_approved") | Q(status="admin_rejected") | Q(status="fin_review")).order_by("-created_at")[:25]
        context["financial_requests"] = FinancialRequest.objects.filter(status="pending")

        return render(request, "employee/FIM.html", context=context)

    elif request.user.role.id == "ADM":
        context["waiting_approval"] = Project.objects.filter(status="fin_review")
        context["project_history"] = Project.objects.filter(Q(status="admin_approved") | Q(status="admin_rejected")).order_by("-created_at")[:25]

        return render(request, "employee/ADM.html", context=context)
    elif request.user.role.id == "PDM" or request.user.role.id == "SDM":
        context["projects"] = Project.objects.filter(status="admin_approved").order_by("-created_at")[:25]

        return render(request, "employee/PSDM.html", context=context)

    elif request.user.role.id == "PDE" or request.user.role.id == "SDE":
        context["tasks"] = Task.objects.filter(completed=False, assignee=request.user).order_by("due_date")[:25]
        context["projects"] = Project.objects.filter(status="admin_approved").order_by("-created_at")[:25]

        return render(request, "employee/PSDE.html", context=context)
    elif request.user.role.id == "HRM":

        if request.method == "POST":
            recruitment_request_id = request.POST.get("recruitment_request_id")
            if recruitment_request_id is None:
                return HttpResponseBadRequest("Invalid request.")

            project = get_object_or_404(RecruitementPost, id=recruitment_request_id)

            if "start_campaign" in request.POST:
                project.status = "ongoing"
                messages.success(request, "Recruitment campaign started successfully.")
            elif "complete_campaign" in request.POST:
                project.status = "completed"
                messages.success(request, "Recruitment campaign completed successfully.")
            else:
                return HttpResponseBadRequest("Invalid request.")

            project.save()

        context["pending_campaigns"] = RecruitementPost.objects.filter(status="pending")
        context["ongoing_campaigns"] = RecruitementPost.objects.filter(status="ongoing")

        return render(request, "employee/HRM.html", context=context)
    # TODO add conditions for other employee types
