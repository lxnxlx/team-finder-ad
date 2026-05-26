from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProfileForm, RegisterForm, TeamFinderPasswordChangeForm
from .models import User


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("projects:list")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


def participants(request):
    users = User.objects.order_by("-id")
    paginator = Paginator(users, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "participants": page_obj.object_list,
        "page_obj": page_obj,
    }
    return render(request, "users/participants.html", context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password(request):
    if request.method == "POST":
        form = TeamFinderPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = TeamFinderPasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})
