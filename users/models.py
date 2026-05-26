from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from team_finder.utils import build_initial_avatar, get_avatar_filename

from .managers import UserManager


USER_NAME_MAX_LENGTH = 124
USER_PHONE_MAX_LENGTH = 12
USER_ABOUT_MAX_LENGTH = 256


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email", unique=True)
    name = models.CharField("имя", max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField("фамилия", max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField("аватар", upload_to="avatars/")
    phone = models.CharField("телефон", max_length=USER_PHONE_MAX_LENGTH, blank=True)
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("о себе", max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ("-id",)
        indexes = [models.Index(fields=["email"])]

    def __str__(self):
        full_name = f"{self.name} {self.surname}".strip()
        if full_name:
            return full_name
        return self.email

    def save(self, *args, **kwargs):
        if not self.avatar:
            file_name = get_avatar_filename()
            avatar_file = build_initial_avatar(file_name, self.name, self.email)
            self.avatar.save(file_name, avatar_file, save=False)
        super().save(*args, **kwargs)
