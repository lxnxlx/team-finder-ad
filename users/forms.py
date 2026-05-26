import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


PHONE_RE = re.compile(r"^(?:8|\+7)\d{10}$")


def normalize_phone(value):
    if value is None:
        return ""

    phone = value.strip()
    if phone.startswith("8") and len(phone) == 11:
        phone = "+7" + phone[1:]
    return phone


def validate_github_url(value):
    if not value:
        return

    parsed_url = urlparse(value)
    host = parsed_url.netloc.lower()
    if host not in {"github.com", "www.github.com"}:
        raise forms.ValidationError("Ссылка должна вести на github.com")


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if not email or not password:
            return cleaned_data

        user = authenticate(username=email, password=password)
        if user is None:
            raise forms.ValidationError("Неверный email или пароль")

        cleaned_data["user"] = user
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data.get("phone"))
        if not phone:
            return phone

        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")

        users_with_same_phone = User.objects.filter(phone=phone)
        if self.instance.pk:
            users_with_same_phone = users_with_same_phone.exclude(pk=self.instance.pk)

        if users_with_same_phone.exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже существует")
        return phone

    def clean_github_url(self):
        value = self.cleaned_data.get("github_url")
        validate_github_url(value)
        return value


class TeamFinderPasswordChangeForm(PasswordChangeForm):
    pass
