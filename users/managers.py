from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if "is_staff" not in extra_fields:
            extra_fields["is_staff"] = True
        if "is_superuser" not in extra_fields:
            extra_fields["is_superuser"] = True
        if "is_active" not in extra_fields:
            extra_fields["is_active"] = True
        if "name" not in extra_fields:
            extra_fields["name"] = "Admin"
        if "surname" not in extra_fields:
            extra_fields["surname"] = "User"

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)
