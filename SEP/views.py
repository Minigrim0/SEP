from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from project.forms import RawRequestForm
from project.models import RawRequest


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
        context["raw_requests"] = RawRequest.objects.filter(project=None)

        return render(request, "employee/CSE.html", context=context)
