import json
import shutil
import tempfile
from http import HTTPStatus

from django.test import TestCase, override_settings
from django.urls import reverse

from projects.models import Project, Skill
from users.models import User


TEMP_MEDIA_ROOT = tempfile.mkdtemp()
TEST_PASSWORD = "pass12345"
JSON_CONTENT_TYPE = "application/json"
DJANGO_SKILL_NAME = "Django"
REACT_SKILL_NAME = "React"
REVIEW_PROJECT_NAME = "Доска ревью"
SPRINT_PROJECT_NAME = "Сервис командных спринтов"
SPRINT_PROJECT_DESCRIPTION = "Планирование pet-проектов по коротким циклам."
SPRINT_PROJECT_GITHUB = "https://github.com/example/team-sprints"
FORBIDDEN_PROJECT_NAME = "Closed scope"
PARTICIPATION_PROJECT_NAME = "Open team"


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProjectFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.owner = self.create_test_user(
            email="owner@example.com",
            name="Ирина",
            surname="Авторова",
        )
        self.member = self.create_test_user(
            email="member@example.com",
            name="Павел",
            surname="Участников",
        )

    def create_test_user(self, email, name, surname):
        return User.objects.create_user(
            email=email,
            password=TEST_PASSWORD,
            name=name,
            surname=surname,
        )

    def test_create_project_sets_owner_and_participant(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": SPRINT_PROJECT_NAME,
                "description": SPRINT_PROJECT_DESCRIPTION,
                "github_url": SPRINT_PROJECT_GITHUB,
                "status": Project.STATUS_OPEN,
            },
        )

        project = Project.objects.get()
        self.assertRedirects(response, reverse("projects:detail", args=[project.id]))
        self.assertEqual(project.owner, self.owner)
        self.assertTrue(project.participants.filter(pk=self.owner.pk).exists())

    def test_project_skills_can_be_created_added_filtered_and_removed(self):
        self.client.force_login(self.owner)
        project = Project.objects.create(name=REVIEW_PROJECT_NAME, owner=self.owner)

        add_response = self.client.post(
            reverse("projects:add_skill", args=[project.id]),
            data=json.dumps({"name": DJANGO_SKILL_NAME}),
            content_type=JSON_CONTENT_TYPE,
        )
        self.assertEqual(add_response.status_code, HTTPStatus.OK)
        self.assertTrue(add_response.json()["created"])
        self.assertTrue(project.skills.filter(name=DJANGO_SKILL_NAME).exists())

        list_response = self.client.get(reverse("projects:list"), {"skill": DJANGO_SKILL_NAME})
        self.assertContains(list_response, REVIEW_PROJECT_NAME)

        skill = Skill.objects.get(name=DJANGO_SKILL_NAME)
        remove_response = self.client.post(reverse("projects:remove_skill", args=[project.id, skill.id]))
        self.assertEqual(remove_response.status_code, HTTPStatus.OK)
        self.assertFalse(project.skills.filter(pk=skill.pk).exists())

    def test_non_owner_cannot_manage_project_skills_or_complete_project(self):
        project = Project.objects.create(name=FORBIDDEN_PROJECT_NAME, owner=self.owner)
        self.client.force_login(self.member)

        add_response = self.client.post(
            reverse("projects:add_skill", args=[project.id]),
            data=json.dumps({"name": REACT_SKILL_NAME}),
            content_type=JSON_CONTENT_TYPE,
        )
        complete_response = self.client.post(reverse("projects:complete", args=[project.id]))

        self.assertEqual(add_response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(complete_response.status_code, HTTPStatus.FORBIDDEN)

    def test_user_can_toggle_participation(self):
        project = Project.objects.create(name=PARTICIPATION_PROJECT_NAME, owner=self.owner)
        self.client.force_login(self.member)

        join_response = self.client.post(reverse("projects:toggle_participate", args=[project.id]))
        leave_response = self.client.post(reverse("projects:toggle_participate", args=[project.id]))

        self.assertTrue(join_response.json()["participant"])
        self.assertFalse(leave_response.json()["participant"])
