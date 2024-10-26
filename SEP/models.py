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
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class Employee(AbstractUser):
    name = models.CharField(max_length=100)
    role = models.ForeignKey("SEP.Role", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name
