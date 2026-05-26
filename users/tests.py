import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from users.forms import ProfileForm
from users.models import User


TEMP_MEDIA_ROOT = tempfile.mkdtemp()
TEST_PASSWORD = "pass12345"
REGISTER_EMAIL = "anna@example.com"
REGISTER_NAME = "Анна"
REGISTER_SURNAME = "Петрова"
FIRST_USER_EMAIL = "first@example.com"
SECOND_USER_EMAIL = "second@example.com"
EXISTING_PHONE = "+79990000000"
VALID_PHONE_INPUT = "89990000001"
VALID_PHONE_RESULT = "+79990000001"
DUPLICATE_PHONE_INPUT = "89990000000"
GITHUB_URL = "https://github.com/example"
AVATAR_PREFIX = "avatars/avatar_"


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
                "surname": REGISTER_SURNAME,
                "email": REGISTER_EMAIL,
                "password": TEST_PASSWORD,
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        user = User.objects.get(email=REGISTER_EMAIL)
        self.assertTrue(user.check_password(TEST_PASSWORD))
        self.assertTrue(user.avatar.name.startswith(AVATAR_PREFIX))

    def test_profile_form_normalizes_phone_and_rejects_duplicate(self):
        existing = User.objects.create_user(
            email=FIRST_USER_EMAIL,
            password=TEST_PASSWORD,
            name="Первый",
            surname="Пользователь",
            phone=EXISTING_PHONE,
        )
        edited = User.objects.create_user(
            email=SECOND_USER_EMAIL,
            password=TEST_PASSWORD,
            name="Второй",
            surname="Пользователь",
        )

        valid_form = ProfileForm(
            data={
                "name": existing.name,
                "surname": existing.surname,
                "about": "",
                "phone": VALID_PHONE_INPUT,
                "github_url": GITHUB_URL,
            },
            instance=existing,
        )
        duplicate_form = ProfileForm(
            data={
                "name": edited.name,
                "surname": edited.surname,
                "about": "",
                "phone": DUPLICATE_PHONE_INPUT,
                "github_url": GITHUB_URL,
            },
            instance=edited,
        )

        self.assertTrue(valid_form.is_valid())
        self.assertEqual(valid_form.cleaned_data["phone"], VALID_PHONE_RESULT)
        self.assertFalse(duplicate_form.is_valid())
