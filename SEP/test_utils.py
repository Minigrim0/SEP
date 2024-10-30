import logging

from project.models import Project, RawRequest
from SEP.models import Customer, Employee, Role

logger = logging.getLogger(__name__)


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

def create_people():
    for role_id, role_name in [
        ("CSE", "Customer Service Employee"),
        ("CSM", "Customer Service Manager"),
        ("FIM", "Financial Manager"),
        ("ADM", "Administration Dpt Manager")
    ]:
        _, created = Role.objects.get_or_create(id=role_id, name=role_name)
        if created:
            logger.info(f"Role {role_name} created.")
        else:
            logger.warn(f"Role {role_name} already exists.")

    # Create initial employees
    if Employee.objects.get_or_create(
        username="cse1",
        first_name="Carmen",
        last_name="Santa-Emeritus",
        email="cse1@sep.se",
        role=Role.objects.get(id="CSE"),
    )[1]:
        logger.info("CSE Employee Carmen Santa-Emeritus created.")
    else:
        logger.warn("CSE Employee Carmen Santa-Emeritus already exists.")

    if Employee.objects.get_or_create(
        username="cse2",
        first_name="Cedric",
        last_name="Saladin-Ernandez",
        email="cse2@sep.se",
        role=Role.objects.get(id="CSE"),
    ):
        logger.info("CSE Employee Cedric Saladin-Ernandez created.")
    else:
        logger.warn("CSE Employee Cedric Saladin-Ernandez already exists.")

    if Employee.objects.get_or_create(
        username="csm1",
        first_name="Carlos",
        last_name="Sitaro-Meritus",
        email="csm1@sep.se",
        role=Role.objects.get(id="CSM"),
    ):
        logger.info("CSM Employee Carlos Sitaro-Meritus created.")
    else:
        logger.warn("CSM Employee Carlos Sitaro-Meritus already exists.")

    if Employee.objects.get_or_create(
        username="fim1",
        first_name="Fernando",
        last_name="Iniesta-Malan",
        email="fim1@sep.se",
        role=Role.objects.get(id="FIM"),
    ):
        logger.info("FIM Employee Fernando Iniesta-Malan created.")
    else:
        logger.warn("FIM Employee Fernando Iniesta-Malan already exists.")

    if Employee.objects.get_or_create(
        username="adm1",
        first_name="Amanda",
        last_name="Dministrador",  # Thanks copilot
        email="adm1@sep.se",
        role=Role.objects.get(id="ADM"),
    ):
        logger.info("ADM Employee Amanda Dministrador created.")
    else:
        logger.warn("ADM Employee Amanda Dministrador already exists.")
