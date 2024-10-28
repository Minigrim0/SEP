from django.db import models
from django.contrib.auth.models import AbstractUser

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self) -> str:
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)
    id = models.CharField(max_length=3, primary_key=True)

    def __str__(self) -> str:
        return self.name


class Employee(AbstractUser):
    role = models.ForeignKey("SEP.Role", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """Add a default role if needed."""

        try:
            if self.role is None:
                self.role = Role.objects.get_or_create(id="CSE", name="Customer Service Employee")[0]
        except Role.DoesNotExist:
            self.role = Role.objects.get_or_create(id="CSE", name="Customer Service Employee")[0]

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.last_name} - {self.first_name} - {self.role.name}"

    def amount_of_projects(self) -> int:
        return self.project_set.count()
