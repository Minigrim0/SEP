import logging

from django.test import TestCase, Client
from django.shortcuts import reverse

from SEP.models import Role, Employee
from SEP.test_utils import create_people, create_project, create_request

logger = logging.getLogger(__name__)

class EmployeeTestCase(TestCase):
    def setUp(self):
        """Create initial data to work from"""

        self.client = Client()
        create_people()

    def test_cse_sees_requests(self):
        """Tests that the CSE can see pending projects."""

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
