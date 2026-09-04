import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create superuser from environment variables if one does not exist"

    def handle(self, *args, **kwargs):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com").strip().lower()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "AdminPass123!")

        user, created = User.objects.get_or_create(email=email, defaults={"name": "Admin"})
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Superuser: {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated Superuser permissions & password for: {email}"))
