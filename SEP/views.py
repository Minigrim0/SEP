from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from project.forms import RawRequestForm
from project.models import RawRequest, Project


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
        context["waiting_feedback"] = Project.objects.filter(status="cs_approved")
        context["project_history"] = Project.objects.filter(Q(status="admin_approved") | Q(status="admin_rejected")).order_by("-created_at")[:25]

        return render(request, "employee/FIM.html", context=context)
    elif request.user.role.id == "ADM":
        context["waiting_approval"] = Project.objects.filter(status="fin_review")
        context["project_history"] = Project.objects.filter(Q(status="admin_approved") | Q(status="admin_rejected")).order_by("-created_at")[:25]

        return render(request, "employee/ADM.html", context=context)

    # TODO add conditions for other employee types
