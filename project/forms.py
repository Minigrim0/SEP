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
        exclude = (
            "initial_request",
            "status",
            "financial_feedback",
            "financial_feedback_draft_status",
            "created_by",
            "meeting",
        )


class FinancialFeedbackForm(forms.Form):
    """Form for the financial manager to write feedback on a project"""

    feedback = forms.CharField(widget=forms.Textarea)
