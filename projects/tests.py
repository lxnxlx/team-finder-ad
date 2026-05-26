import json
import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from projects.models import Project, Skill
from users.models import User


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProjectFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass12345",
            name="Ирина",
            surname="Авторова",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="pass12345",
            name="Павел",
            surname="Участников",
        )

    def test_create_project_sets_owner_and_participant(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "Сервис командных спринтов",
                "description": "Планирование pet-проектов по коротким циклам.",
                "github_url": "https://github.com/example/team-sprints",
                "status": Project.STATUS_OPEN,
            },
        )

        project = Project.objects.get()
        self.assertRedirects(response, reverse("projects:detail", args=[project.id]))
        self.assertEqual(project.owner, self.owner)
        self.assertTrue(project.participants.filter(pk=self.owner.pk).exists())

    def test_project_skills_can_be_created_added_filtered_and_removed(self):
        self.client.force_login(self.owner)
        project = Project.objects.create(name="Доска ревью", owner=self.owner)

        add_response = self.client.post(
            reverse("projects:add_skill", args=[project.id]),
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertTrue(add_response.json()["created"])
        self.assertTrue(project.skills.filter(name="Django").exists())

        list_response = self.client.get(reverse("projects:list"), {"skill": "Django"})
        self.assertContains(list_response, "Доска ревью")

        skill = Skill.objects.get(name="Django")
        remove_response = self.client.post(reverse("projects:remove_skill", args=[project.id, skill.id]))
        self.assertEqual(remove_response.status_code, 200)
        self.assertFalse(project.skills.filter(pk=skill.pk).exists())

    def test_non_owner_cannot_manage_project_skills_or_complete_project(self):
        project = Project.objects.create(name="Closed scope", owner=self.owner)
        self.client.force_login(self.member)

        add_response = self.client.post(
            reverse("projects:add_skill", args=[project.id]),
            data=json.dumps({"name": "React"}),
            content_type="application/json",
        )
        complete_response = self.client.post(reverse("projects:complete", args=[project.id]))

        self.assertEqual(add_response.status_code, 403)
        self.assertEqual(complete_response.status_code, 403)

    def test_user_can_toggle_participation(self):
        project = Project.objects.create(name="Open team", owner=self.owner)
        self.client.force_login(self.member)

        join_response = self.client.post(reverse("projects:toggle_participate", args=[project.id]))
        leave_response = self.client.post(reverse("projects:toggle_participate", args=[project.id]))

        self.assertTrue(join_response.json()["participant"])
        self.assertFalse(leave_response.json()["participant"])
