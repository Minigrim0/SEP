from django.core import validators
from django.db import models
from django.utils import timezone


class RawRequest(models.Model):
    """A raw request from a client. This needs to be processed by the customer service team."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    description = models.TextField()
    available = models.IntegerField(verbose_name="Available budget", validators=[validators.MinValueValidator(0)])


class Meeting(models.Model):
    date = models.DateField(verbose_name="Meeting date")
    time = models.TimeField(verbose_name="Meeting time")

    members = models.ManyToManyField("SEP.Employee", verbose_name="Meeting members (excl. client)")

    def __str__(self) -> str:
        return f"Meeting {self.date} - {self.time} ({self.project})"


class Project(models.Model):
    STATUS_CHOICES = [
        ("draft", "DRAFT"),  # Initial state, the CS team Started filling the form
        ("pending", "PENDING"),  # The CS team filled the form from the client request
        ("cs_approved", "APPROVED BY CUSTOMER SERVICE"),  # The CS Senior approved the project
        ("cs_rejected", "REJECTED BY CUSTOMER SERVICE"),  # The CS Senior approved the project
        ("fin_review", "REVIEWED BY THE FINANCIAL MANAGER"),  # The financial manager reviewed the project and wrote some feedback
        ("admin_approved", "APPROVED BY THE ADMINISTRATION MANAGER"),  # The admin manager approved the project
        ("admin_rejected", "REJECTED BY THE ADMINISTRATION MANAGER"),  # The admin manager rejected the project
    ]

    # Information on the client
    client = models.ForeignKey("SEP.Customer", verbose_name="Project client", blank=True, null=True, on_delete=models.CASCADE)
    initial_request = models.OneToOneField("project.RawRequest", verbose_name="Initial request", blank=True, null=True, on_delete=models.CASCADE)

    # Information on the project
    title = models.CharField(verbose_name="Project Title", max_length=100)
    description = models.TextField(verbose_name="Project Description", blank=True, null=True)
    estimated_budget = models.IntegerField(verbose_name="Initial budget estimation", validators=[validators.MinValueValidator(0)], blank=True, null=True)

    # Information on the project status
    status = models.CharField(verbose_name="project status", max_length=20, choices=STATUS_CHOICES, default="draft", blank=True, null=True)

    financial_feedback = models.TextField(verbose_name="feedback from financial dpt.", blank=True, null=True)

    meeting = models.OneToOneField("project.Meeting", verbose_name="Initial client meeting", on_delete=models.CASCADE, blank=True, null=True)

    created_by = models.ForeignKey("SEP.Employee", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.status} - {self.title}"
