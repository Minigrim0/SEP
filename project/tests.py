import logging

from django.shortcuts import reverse
from django.test import TestCase, Client
from SEP.models import Role, Employee, Customer
from SEP.test_utils import create_project
from project.models import RawRequest, Project

logger = logging.getLogger(__name__)


class ProjectTestCase(TestCase):
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


    def test_create_project_from_raw(self):
        """Tests that the form to create a project from a raw request works correctly."""
        self.client.force_login(Employee.objects.get(username="cse1"))

        request, _ = RawRequest.objects.get_or_create(
            name="some_dude",
            email="some_dude@gmail.com",
            phone="0123456789",
            address="Some street, 123",
            title="I want some event planned",
            description="Lie a really big event",
            available=10000
        )

        # Employee should be able to access the form
        self.assertTrue(200, self.client.get(reverse("project:project_from_raw", args=[request.id])).status_code)

        # Employee should be able to submit the form to save a draft
        response = self.client.post(reverse("project:project_from_raw", args=[request.id]), {
            "client": Customer.objects.get_or_create(
                name="some_dude",
                email="some_dude@gmail.com",
                phone="0123456789",
                address="Some street, 123",
            )[0].id,
            "title": "I want some event planned",
            "description": "Lie a really big event",
            "estimated_budget": 10000,
            "save_draft": ""
        })

        # Test that the project was created and saved as draft
        self.assertTrue(302, response.status_code)
        self.assertIsNotNone(request.project)
        # Test typo
        self.assertEqual("Lie a really big event", request.project.description)
        self.assertEqual("draft", request.project.status)

        # Employee should be able to submit the form to submit the project for the CSM to review
        response = self.client.post(reverse("project:project_from_raw", args=[request.id]), {
            "client": Customer.objects.get_or_create(
                name="some_dude",
                email="some_dude@gmail.com",
                phone="0123456789",
                address="Some street, 123",
            )[0].id,
            "title": "I want some event planned",
            "description": "Like a really big event",
            "estimated_budget": 10000,
            "publish_project": ""
        })

        project = Project.objects.get(initial_request=request)

        # Test that the project was created and saved as pending
        self.assertTrue(302, response.status_code)
        self.assertEqual("Like a really big event", project.description)
        self.assertEqual("pending", project.status)


    def test_csm_approves_project(self):
        """Tests that the CSM can approve a project."""

        self.client.force_login(Employee.objects.get(username="csm1"))

        project = create_project()

        response = self.client.get(f"{reverse('project:csm_action', args=[project.id])}?approve=1")

        self.assertEqual(302, response.status_code)
        self.assertEqual("cs_approved", Project.objects.get(id=project.id).status)

    def test_csm_rejects_project(self):
        """Tests that the CSM can reject a project."""

        self.client.force_login(Employee.objects.get(username="csm1"))

        project = create_project()

        response = self.client.get(f"{reverse('project:csm_action', args=[project.id])}?approve=0")

        self.assertEqual(302, response.status_code)
        self.assertEqual("cs_rejected", Project.objects.get(id=project.id).status)

    def test_fin_writes_feedback(self):
        """Tests that the Finance Manager can write feedback to a project."""

        # Create an approved project for the FIM to write feedback on
        project = create_project()
        project.status = "cs_approved"
        project.save()

        self.client.force_login(Employee.objects.get(username="fim1"))

        feedback = "This project is too expensive, please reduce the budget."
        response = self.client.post(reverse("project:fin_action", args=[project.id]), {
            "feedback": feedback
        })

        self.assertEqual(302, response.status_code)
        self.assertEqual("fin_review", Project.objects.get(id=project.id).status)
        self.assertEqual(feedback, Project.objects.get(id=project.id).financial_feedback)

    def test_adm_approves_project(self):
        """Tests that the Admin can approve a project."""

        project = create_project()
        project.status = "fin_review"
        project.save()

        self.client.force_login(Employee.objects.get(username="adm1"))

        response = self.client.get(f"{reverse('project:adm_action', args=[project.id])}?approve=1")

        self.assertEqual(302, response.status_code)
        self.assertEqual("admin_approved", Project.objects.get(id=project.id).status)

    def test_adm_rejects_project(self):
        """Tests that the Admin can reject a project."""

        project = create_project()
        project.status = "fin_review"
        project.save()

        self.client.force_login(Employee.objects.get(username="adm1"))

        response = self.client.get(f"{reverse('project:adm_action', args=[project.id])}?approve=0")

        self.assertEqual(302, response.status_code)
        self.assertEqual("admin_rejected", Project.objects.get(id=project.id).status)
