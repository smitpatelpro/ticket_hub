from rest_framework.test import APIClient
from django.test import TestCase

from apps.common.models import CustomUser
from apps.v1.comments.models import Comment
from apps.v1.projects.models import Project, ProjectMembership
from apps.v1.tasks.models import Task


class CommentCombinedTestCase(TestCase):
    """
    Unit test cases for Comment model
    """

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
            "project_id": str(self.proj1.id),
            "assignee_id": str(self.user1.id),
        }
        self.task_data2 = {
            "title": "Test",
            "description": "NEW ***Task***",
            "status": "TODO",
            "project_id": str(self.proj2.id),
            "assignee_id": str(self.user2.id),
        }
        self.task1 = Task.objects.create(**self.task_data1)
        self.task2 = Task.objects.create(**self.task_data2)

        self.COMMENT_LIST_API_URL = "/api/v1/projects/{}/tasks/{}/comments/"
        self.COMMENT_DETAIL_API_URL = "/api/v1/projects/{}/tasks/{}/comments/{}/"
        

    def test_comment_creation(self):
        comment = Comment.objects.create(
            task=self.task1,
            author=self.user1,
            content="This is a test comment",
        )
        self.assertEqual(comment.task, self.task1)
        self.assertEqual(comment.author, self.user1)
        self.assertEqual(comment.content, "This is a test comment")

    def test_comment_deletion(self):
        comment = Comment.objects.create(
            task=self.task1,
            author=self.user1,
            content="This is a test comment",
        )
        comment.delete()
        self.assertFalse(Comment.objects.filter(task=self.task1).exists())


    def test_comment_soft_deletion(self):
        comment = Comment.objects.create(
            task=self.task1,
            author=self.user1,
            content="This is a test comment",
        )
        comment.soft_delete()
        self.assertFalse(Comment.objects.existing().filter(task=self.task1).exists())

    def test_comment_update(self):
        comment = Comment.objects.create(
            task=self.task1,
            author=self.user1,
            content="This is a test comment",
        )
        comment.content = "This is an updated test comment"
        comment.save()
        self.assertEqual(Comment.objects.get(task=self.task1).content, "This is an updated test comment")

    
    def test_comment_creation_api(self):
        comment_data = {
            "task": str(self.task1.id),
            "author": str(self.user1.id),
            "content": "This is a test comment",
        }
        response = self.client.post(self.COMMENT_LIST_API_URL.format(self.proj1.id, self.task1.id), comment_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["task"], str(self.task1.id))
        self.assertEqual(response.data["author"], str(self.user1.id))
        self.assertEqual(response.data["content"], "This is a test comment")

    # def test_comment_deletion_api(self):
    #     comment = Comment.objects.create(
    #         task=self.task1,
    #         author=self.user1,
    #         content="This is a test comment",
    #     )
    #     response = self.client.delete(
    #        self.COMMENT_DETAIL_API_URL.format(self.proj1.id, self.task1.id, comment.id)
    #     )
    #     self.assertEqual(response.status_code, 204)
    #     self.assertFalse(Comment.objects.filter(task=self.task1, id=comment.id).exists())

    def test_comment_soft_deletion_api(self):
        comment = Comment.objects.create(
            task=self.task1,
            author=self.user1,
            content="This is a test comment",
        )
        response = self.client.delete(
            self.COMMENT_DETAIL_API_URL.format(self.proj1.id, self.task1.id, comment.id)
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.existing().filter(task=self.task1).exists())

    def test_comment_update_api(self):
        comment = Comment.objects.create(
            task=self.task1,
            author=self.user1,
            content="This is a test comment",
        )
        comment_data = {
            "task": str(self.task1.id),
            "author": str(self.user1.id),
            "content": "This is an updated test comment",
        }
        response = self.client.patch(
            self.COMMENT_DETAIL_API_URL.format(self.proj1.id, self.task1.id, comment.id),
            comment_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Comment.objects.get(task=self.task1).content,
            "This is an updated test comment",
        )
