from django.conf import settings
from django.db import models


class Skill(models.Model):
    name = models.CharField("название навыка", max_length=124, unique=True)

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]

    name = models.CharField("название", max_length=200)
    description = models.TextField("описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="автор",
    )
    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    github_url = models.URLField("GitHub", blank=True)
    status = models.CharField("статус", max_length=6, choices=STATUS_CHOICES, default=STATUS_OPEN)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="участники",
    )
    skills = models.ManyToManyField(Skill, related_name="projects", blank=True, verbose_name="навыки")

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name
