from django import forms

from project.models import RawRequest, Project


class RawRequestForm(forms.ModelForm):
    """Form for customer to request a service."""

    class Meta:
        model = RawRequest
        fields = "__all__"


class ProjectInitialForm(forms.ModelForm):
    """Form for the CS emplyee to create a new project."""

    class Meta:
        model = Project
        # Only these fields are required to be filled by the CS employee
        fields = ("title", "client", "description", "estimated_budget", )
        exclude = (
            "initial_request",
            "status",
            "financial_feedback",
            "meeting"
        )
