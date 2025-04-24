from rest_framework.test import APIClient
from rest_framework import exceptions
from django.test import TestCase
from apps.common.models import CustomUser
from apps.v1.projects.models import Project, ProjectMembership
from apps.v1.tasks.models import Task


class TaskUnitTestCase(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Test project")
        self.task = Task.objects.create(
            project=self.project,
            title="Test task",
            description="This is a test task",
            creator=CustomUser.objects.create(username="test_user"),
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, "Test task")
        self.assertEqual(self.task.description, "This is a test task")
        self.assertEqual(self.task.creator.username, "test_user")

    def test_task_update(self):
        self.task.title = "Updated test task"
        self.task.save()
        self.assertEqual(self.task.title, "Updated test task")

    def test_task_deletion(self):
        self.task.delete()
        self.assertFalse(Task.objects.filter(title="Test task").exists())


class TaskIntegrationTestCase(TestCase):
    def setUp(self):
        print("Setting up api client")
        self.user1 = CustomUser.objects.create(
            username="jon_doe", email="jon_doe@domain.com"
        )
        self.user2 = CustomUser.objects.create(
            username="jon_doe2", email="jon_doe2@domain.com"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        self.proj1 = Project.objects.create(title="Test project 1")
        self.proj2 = Project.objects.create(title="Test project 2")

        ProjectMembership.objects.create(
            user=self.user1,
            project=self.proj1,
        )
        ProjectMembership.objects.create(
            user=self.user2,
            project=self.proj2,
        )

        self.task_data1 = {
            "title": "Test",
            "description": "NEW ***Task***",
            "status": "TODO",
            "project": str(self.proj1.id),
            "assignee": str(self.user1.id),
        }
        self.task_data2 = {
            "title": "Test",
            "description": "NEW ***Task***",
            "status": "TODO",
            "project": str(self.proj2.id),
            "assignee": str(self.user2.id),
        }

    def test_task_create_list(self):
        r = self.client.post(
            "/api/v1/projects/{}/tasks/".format(self.proj1.id),
            self.task_data1,
        )
        print(r.data)
        r = self.client.post(
            "/api/v1/projects/{}/tasks/".format(self.proj2.id),
            self.task_data2,
        )
        print(r.data)

        response = self.client.get("/api/v1/projects/{}/tasks/".format(self.proj1.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_task_update(self):
        task = self.client.post(
            "/api/v1/projects/{}/tasks/".format(self.proj1.id),
            self.task_data1,
        )

        task_id = task.data["id"]
        response = self.client.patch(
            "/api/v1/projects/{}/tasks/{}/".format(self.proj1.id, task_id),
            {
                **self.task_data1,
                "title": "Test task updated",
            },
        )

        response = self.client.get(
            "/api/v1/projects/{}/tasks/{}/".format(self.proj1.id, task_id),
            {
                **self.task_data1,
                "title": "Test task updated",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test task updated")

    def test_task_deletion(self):
        task = self.client.post(
            "/api/v1/projects/{}/tasks/".format(self.proj1.id),
            self.task_data1,
        )
        task_id = task.data["id"]
        response = self.client.delete(
            "/api/v1/projects/{}/tasks/{}/".format(self.proj1.id, task_id)
        )
        self.assertEqual(response.status_code, 204)

        # Object should not be available after deletion
        self.assertFalse(Task.objects.existing().filter(id=task_id))

    def test_task_soft_deletion(self):
        task = self.client.post(
            "/api/v1/projects/{}/tasks/".format(self.proj1.id),
            self.task_data1,
        )
        task_id = task.data["id"]
        response = self.client.delete(
            "/api/v1/projects/{}/tasks/{}/".format(self.proj1.id, task_id)
        )
        self.assertEqual(response.status_code, 204)

        # Object should be available even after deletion
        self.assertTrue(Task.objects.all().filter(id=task_id))
