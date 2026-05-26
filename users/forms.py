from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from team_finder.utils import normalize_phone, validate_github_url, validate_phone_format

from .models import User


ABOUT_TEXTAREA_ROWS = 4


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
            "about": forms.Textarea(attrs={"rows": ABOUT_TEXTAREA_ROWS}),
        }

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data.get("phone"))
        if not phone:
            return phone

        validate_phone_format(phone)

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
