from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from project.forms import RawRequestForm

def home(request):
    request_form = RawRequestForm()

    return render(request, "index.html", context={"form": request_form})


@login_required
def employee_home(request):
    return render(request, "employee.html")
