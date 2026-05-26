import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from users.forms import ProfileForm
from users.models import User


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_register_creates_email_login_user(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Анна",
                "surname": "Петрова",
                "email": "anna@example.com",
                "password": "pass12345",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        user = User.objects.get(email="anna@example.com")
        self.assertTrue(user.check_password("pass12345"))
        self.assertTrue(user.avatar.name.startswith("avatars/avatar_"))

    def test_profile_form_normalizes_phone_and_rejects_duplicate(self):
        existing = User.objects.create_user(
            email="first@example.com",
            password="pass12345",
            name="Первый",
            surname="Пользователь",
            phone="+79990000000",
        )
        edited = User.objects.create_user(
            email="second@example.com",
            password="pass12345",
            name="Второй",
            surname="Пользователь",
        )

        valid_form = ProfileForm(
            data={
                "name": existing.name,
                "surname": existing.surname,
                "about": "",
                "phone": "89990000001",
                "github_url": "https://github.com/example",
            },
            instance=existing,
        )
        duplicate_form = ProfileForm(
            data={
                "name": edited.name,
                "surname": edited.surname,
                "about": "",
                "phone": "89990000000",
                "github_url": "https://github.com/example",
            },
            instance=edited,
        )

        self.assertTrue(valid_form.is_valid())
        self.assertEqual(valid_form.cleaned_data["phone"], "+79990000001")
        self.assertFalse(duplicate_form.is_valid())
