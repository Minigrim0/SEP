from django import forms

from project.models import RawRequest


class RawRequestForm(forms.ModelForm):
    """Form for customer to request a service."""

    class Meta:
        model = RawRequest
        fields = "__all__"
