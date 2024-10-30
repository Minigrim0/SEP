from django import forms

from project.models import RawRequest, Project, Task
from SEP.models import Employee


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
        widgets = {
            "estimated_budget": forms.NumberInput(attrs={"min": 0}),
            "expected_number_of_guests": forms.NumberInput(attrs={"min": 0}),
            "from_date": forms.DateInput(attrs={"type": "date"}),
            "to_date": forms.DateInput(attrs={"type": "date"}),
        }


class FinancialFeedbackForm(forms.Form):
    """Form for the financial manager to write feedback on a project"""

    feedback = forms.CharField(widget=forms.Textarea)


class TaskAssignmentForm(forms.ModelForm):
    """Form for the project manager to assign tasks to a team."""

    class Meta:
        model = Task
        fields = ("assignee", "subject", "priority", "due_date", "description", "due_date")
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "project": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
       	# Extract the user from the view
        team = kwargs.pop('team')
        super().__init__(*args, **kwargs)
        # Filter authors related to the logged-in user

        self.fields['assignee'].queryset = team.members.all()
