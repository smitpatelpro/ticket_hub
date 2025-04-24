from rest_framework.test import APIClient
from rest_framework import exceptions
from django.test import TestCase
from apps.common.models import CustomUser
from apps.v1.projects.models import Project
from apps.v1.projects.serializers import ProjectSerializer


class ProjectUnitTestCase(TestCase):
    def test_project_creation(self):
        project = Project.objects.create(title="Test project")
        self.assertEqual(project.title, "Test project")

    def test_project_deletion(self):
        project = Project.objects.create(title="Test project")
        project.delete()
        self.assertFalse(Project.objects.filter(title="Test project").exists())

    def test_project_soft_deletion(self):
        project = Project.objects.create(title="Test project")
        project.soft_delete()
        self.assertFalse(
            Project.objects.existing().filter(title="Test project").exists()
        )

    def test_project_update(self):
        project = Project.objects.create(title="Test project")
        project.title = "Updated test project"
        project.save()
        self.assertEqual(project.title, "Updated test project")

    def test_project_serialization(self):
        Project.objects.create(title="Test project 1")
        Project.objects.create(title="Test project 2")

        projects = Project.objects.existing()

        serializer = ProjectSerializer(projects, many=True)
        data = serializer.data
        self.assertEqual(len(data), 2)


class ProjectIntegrationTestCase(TestCase):
    def setUp(self):
        print("Setting up api client")

        self.proj1 = Project.objects.create(title="Test project 1")
        self.proj2 = Project.objects.create(title="Test project 2")

        self.client = APIClient()
        self.user = CustomUser.objects.create(
            username="jon_doe", email="jon_doe@domain.com"
        )
        self.user2 = CustomUser.objects.create(
            username="jon_doe2", email="jon_doe2@domain.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_project_creation(self):
        project_dict = {"title": "Project 1", "description": "U1's Project"}
        url = "/api/v1/projects/"
        self.client.post(url, project_dict)

        project_dict["title"] = "Project 2"
        self.client.post(url, project_dict)

        project_dict["title"] = "Project 3"
        self.client.post(url, project_dict)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_member_accept_invitation(self):
        url = "/api/v1/projects/invite/"
        project = self.proj1
        payload = {"user": str(self.user2.id), "project": str(project.id)}
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["invitation_status"], "PENDING")

        invite_id = response.data['id']

        # Accept Request by Sender should return error
        url = f"/api/v1/projects/invite/{invite_id}/action/accept/"
        response = self.client.post(url, payload)
        error_detail: exceptions.ErrorDetail = response.data["detail"]

        self.assertEqual(response.status_code, 403)
        self.assertEqual(error_detail.code, 'permission_denied')

        # Accept Request by Receiver should be successful
        self.client.force_authenticate(user=self.user2)
        url = f"/api/v1/projects/invite/{invite_id}/action/accept/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ACTIVE")

    def test_member_reject_invitation(self):
        url = "/api/v1/projects/invite/"
        project = self.proj1
        payload = {"user": str(self.user2.id), "project": str(project.id)}
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["invitation_status"], "PENDING")

        invite_id = response.data['id']

        # Reject Request by Sender should return error
        url = f"/api/v1/projects/invite/{invite_id}/action/reject/"
        response = self.client.post(url, payload)
        error_detail: exceptions.ErrorDetail = response.data["detail"]

        self.assertEqual(response.status_code, 403)
        self.assertEqual(error_detail.code, 'permission_denied')

        # Reject Request by Receiver should be successful
        self.client.force_authenticate(user=self.user2)
        url = f"/api/v1/projects/invite/{invite_id}/action/reject/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["invitation_status"], "REJECTED")
