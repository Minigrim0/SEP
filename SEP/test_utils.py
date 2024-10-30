from project.models import Project, RawRequest
from SEP.models import Customer, Employee


def create_project() -> Project:
    """Create a project for testing purposes."""

    return Project.objects.get_or_create(
        title="Test project",
        description="A test project",
        client=Customer.objects.get_or_create(
            name="Test client",
            email="test@client.com",
            phone="0123456789",
            address="Test street, 123"
        )[0],
        created_by=Employee.objects.get(username="cse1"),
        status="pending",
        estimated_budget=10000
    )[0]


def create_request() -> RawRequest:
    """Create a request for testing purposes."""

    return RawRequest.objects.get_or_create(
        name="Test request",
        email="requester@test.com",
        phone="0123456789",
        address="Request street, 123",
        title="I want some event planned",
        description="Like a really big event",
        available=10000
    )[0]
