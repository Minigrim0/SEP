import logging

from django.shortcuts import reverse
from django.test import TestCase, Client
from SEP.models import Role, Employee, Customer
from SEP.test_utils import create_project, create_people
from project.models import RawRequest, Project

logger = logging.getLogger(__name__)


class ProjectTestCase(TestCase):
    def setUp(self):
        """Create initial data to work from"""

        self.client = Client()
        create_people()

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


class TaskDispatchingTestCase(TestCase):
    """Tests the task dispatching functionality."""

    def setUp(self):
        """Creates the necessary employees and customers for the tests."""

        create_people()
