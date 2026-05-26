from io import BytesIO
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email", unique=True)
    name = models.CharField("имя", max_length=124)
    surname = models.CharField("фамилия", max_length=124)
    avatar = models.ImageField("аватар", upload_to="avatars/")
    phone = models.CharField("телефон", max_length=12, blank=True)
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("о себе", max_length=256, blank=True)
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
            file_name = self._avatar_filename()
            avatar_file = self._build_initial_avatar(file_name)
            self.avatar.save(file_name, avatar_file, save=False)
        super().save(*args, **kwargs)

    def _avatar_filename(self):
        return f"avatar_{uuid.uuid4()}.png"

    def _build_initial_avatar(self, file_name):
        colors = ["#3A7D7C", "#7A5C99", "#9C6B30", "#3F6EA8", "#5F7A3D", "#8B4A54"]
        text_for_color = self.email
        if not text_for_color:
            text_for_color = self.name

        total = 0
        for symbol in text_for_color:
            total += ord(symbol)
        color_number = total % len(colors)
        color = colors[color_number]

        image = Image.new("RGB", (256, 256), color)
        draw = ImageDraw.Draw(image)

        if self.name:
            letter = self.name[0]
        elif self.email:
            letter = self.email[0]
        else:
            letter = "?"
        letter = letter.upper()

        try:
            font = ImageFont.truetype("Arial.ttf", 128)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        x = (256 - (bbox[2] - bbox[0])) / 2
        y = (256 - (bbox[3] - bbox[1])) / 2 - 8
        draw.text((x, y), letter, fill="white", font=font)

        output = BytesIO()
        image.save(output, format="PNG")
        return ContentFile(output.getvalue(), name=file_name)
