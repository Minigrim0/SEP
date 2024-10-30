import logging

from django.test import TestCase, Client
from django.shortcuts import reverse

from SEP.models import Role, Employee
from SEP.test_utils import create_project, create_request

logger = logging.getLogger(__name__)

class EmployeeTestCase(TestCase):
    def setUp(self):
        """Create initial data to work from"""

        self.client = Client()

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

    def test_cse_sees_requests(self):
        """Tests that the CSM can see pending projects."""

        self.client.force_login(Employee.objects.get(username="cse1"))

        request = create_request()

        response = self.client.get(reverse("employee_home"))

        self.assertEqual(200, response.status_code)
        self.assertIn(request, response.context["raw_requests"])

    def test_csm_sees_pending_projects(self):
        """Tests that the CSM can see pending projects."""

        self.client.force_login(Employee.objects.get(username="csm1"))

        project = create_project()

        response = self.client.get(reverse("employee_home"))

        self.assertEqual(200, response.status_code)
        self.assertIn(project, response.context["waiting_approval"])
