import logging

from django.shortcuts import reverse
from django.test import TestCase, Client

from SEP.test_utils import create_project, create_people
from SEP.models import Role, Employee, Customer
from project.models import RawRequest, Project, Task, RecruitementPost, FinancialRequest

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

        self.client = Client()
        create_people()

    def test_sdm_creates_task(self):
        """Tests that a Service Dpt Manager can create a task and assign it to an employee."""
        sdm1 = Employee.objects.get(username="sdm1")

        self.client.force_login(sdm1)

        project = create_project()
        project.status = "admin_approved"
        project.save()

        sdm1_team = sdm1.managed_teams.first()

        response = self.client.get(reverse("project:psdm_team_action", args=[project.id, sdm1_team.id]))

        self.assertEqual(200, response.status_code)

        response = self.client.post(reverse("project:psdm_team_action", args=[project.id, sdm1_team.id]), {
            "assignee": sdm1_team.members.first().id,
            "subject": "This is a task",
            "priority": 2,
            "due_date": "2024-12-12",
            "description": "This is a description",
        })

        # Check that a task was created
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, Task.objects.filter(project=project).count())

        # Test that invalid values are not accepted
        response = self.client.post(reverse("project:psdm_team_action", args=[project.id, sdm1_team.id]), {
            "assignee": sdm1_team.members.first().id,
            "subject": "This is a task",
            "priority": 98404,
            "due_date": "2024-12-12",
            "description": "This is a description",
        })

        # Check that we are back on the same page (no redirect) and that the form has errors
        self.assertEqual(200, response.status_code)
        self.assertGreaterEqual(len(response.context["form"].errors), 1)

    def test_sde_sees_tasks(self):
        """Tests that a Service/Production Dpt Employee can see new tasks assigned to them."""

        sdm1 = Employee.objects.get(username="sdm1")
        assignee = Employee.objects.get(username="cook1")

        self.client.force_login(sdm1)

        project = create_project()
        project.status = "admin_approved"
        project.save()
        sdm1_team = sdm1.managed_teams.first()

        # This is tested above
        response = self.client.post(reverse("project:psdm_team_action", args=[project.id, sdm1_team.id]), {
            "assignee": assignee.id,
            "subject": "This is a task",
            "priority": 2,
            "due_date": "2024-12-12",
            "description": "This is a description",
        })

        # Just to be sure
        self.assertEqual(302, response.status_code)

        self.client.force_login(assignee)

        response = self.client.get(reverse("employee_home"))
        self.assertEqual(1, response.context["tasks"].count())
        self.assertEqual(sdm1, response.context["tasks"].first().sender)


class RecruitmentPostTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        create_people()

    def test_psdm_create_recruitment_post(self):
        """Tests that a PSDM can create a recruitment post for the HR department."""
        sdm1 = Employee.objects.get(username="sdm1")

        self.client.force_login(sdm1)

        response = self.client.post(reverse("project:recruitement_request"), {
            "contract_type": "full",
            "department": "adm",
            "min_years_experience": 2,
            "title": "Project Co-manager",
            "description": "Co-manage projects"
        })

        self.assertEqual(302, response.status_code)
        self.assertEqual(1, RecruitementPost.objects.count())
        self.assertEqual("adm", RecruitementPost.objects.first().department)
        self.assertEqual("pending", RecruitementPost.objects.first().status)

    def test_hr_start_recruitment(self):
        """Tests that the HR department can start a recruitment process."""
        sdm1 = Employee.objects.get(username="sdm1")

        self.client.force_login(sdm1)

        response = self.client.post(reverse("project:recruitement_request"), {
            "contract_type": "full",
            "department": "adm",
            "min_years_experience": 2,
            "title": "Project Co-manager",
            "description": "Co-manage projects"
        })

        hrm1 = Employee.objects.get(username="hrm1")

        self.client.force_login(hrm1)

        response = self.client.get(reverse("employee_home"))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["pending_campaigns"].count())
        self.assertEqual(0, response.context["ongoing_campaigns"].count())

        response = self.client.post(reverse("employee_home"), {
            "recruitment_request_id": RecruitementPost.objects.first().id,
            "start_campaign": ""
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, response.context["pending_campaigns"].count())
        self.assertEqual(1, response.context["ongoing_campaigns"].count())

    def test_hr_complete_recruitment_campaign(self):
        """Tests that the HR department can finish a recruitment."""

        sdm1 = Employee.objects.get(username="sdm1")

        self.client.force_login(sdm1)

        response = self.client.post(reverse("project:recruitement_request"), {
            "contract_type": "full",
            "department": "adm",
            "min_years_experience": 2,
            "title": "Project Co-manager",
            "description": "Co-manage projects"
        })

        hrm1 = Employee.objects.get(username="hrm1")

        self.client.force_login(hrm1)

        response = self.client.get(reverse("employee_home"))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["pending_campaigns"].count())
        self.assertEqual(0, response.context["ongoing_campaigns"].count())

        # It is possible to skip the start of the recruitment campaign by setting
        # `complete_campaign` in the parameters of the POST request. This can easily
        # be fixed by checking the status of the recruitment post before completing it.
        response = self.client.post(reverse("employee_home"), {
            "recruitment_request_id": RecruitementPost.objects.first().id,
            "complete_campaign": ""
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, response.context["pending_campaigns"].count())
        self.assertEqual(0, response.context["ongoing_campaigns"].count())


class FinancialRequestTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        create_people()

    def test_psdm_create_financial_request(self):
        """Tests that a PSDM can create a financial request."""
        sdm1 = Employee.objects.get(username="sdm1")

        self.client.force_login(sdm1)

        project = create_project()

        response = self.client.post(reverse("project:financial_request", args=[project.id]), {
            "requesting_department": "prod",
            "amount": 1000,
            "reason": "We need money for this project"
        })

        self.assertEqual(302, response.status_code)
        self.assertEqual(1, FinancialRequest.objects.count())
        self.assertEqual("pending", FinancialRequest.objects.first().status)
        self.assertEqual(project, FinancialRequest.objects.first().project)

    def test_fim_approve_financial_request(self):
        """Tests that the financial manager can approve or reject a financial request."""
        sdm1 = Employee.objects.get(username="sdm1")

        self.client.force_login(sdm1)

        project = create_project()

        response = self.client.post(reverse("project:financial_request", args=[project.id]), {
            "requesting_department": "prod",
            "amount": 1000,
            "reason": "We need money for this project"
        })

        fim1 = Employee.objects.get(username="fim1")

        self.client.force_login(fim1)

        # Check that the financial request is sent to the financial manager
        response = self.client.get(reverse("employee_home"))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["financial_requests"].count())

        response = self.client.post(reverse("employee_home"), {
            "fin_request_id": FinancialRequest.objects.first().id,
            "approve_fin": ""
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, response.context["financial_requests"].count())
        self.assertEqual("approved", FinancialRequest.objects.first().status)

    def test_fim_reject_financial_request(self):
        """Tests that the financial manager can approve or reject a financial request."""
        sdm1 = Employee.objects.get(username="sdm1")

        self.client.force_login(sdm1)

        project = create_project()

        response = self.client.post(reverse("project:financial_request", args=[project.id]), {
            "requesting_department": "prod",
            "amount": 1000,
            "reason": "We need money for this project"
        })

        fim1 = Employee.objects.get(username="fim1")

        self.client.force_login(fim1)

        # Check that the financial request is sent to the financial manager
        response = self.client.get(reverse("employee_home"))

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.context["financial_requests"].count())

        response = self.client.post(reverse("employee_home"), {
            "fin_request_id": FinancialRequest.objects.first().id,
            "reject_fin": ""
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, response.context["financial_requests"].count())
        self.assertEqual("rejected", FinancialRequest.objects.first().status)
