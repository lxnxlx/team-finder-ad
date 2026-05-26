from django import forms

from team_finder.utils import validate_github_url

from .models import Project


PROJECT_DESCRIPTION_ROWS = 6


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": PROJECT_DESCRIPTION_ROWS}),
            "status": forms.Select(choices=[
                (Project.STATUS_OPEN, "Открыт"),
                (Project.STATUS_CLOSED, "Закрыт"),
            ]),
        }

    def clean_github_url(self):
        value = self.cleaned_data.get("github_url")
        validate_github_url(value)
        return value
