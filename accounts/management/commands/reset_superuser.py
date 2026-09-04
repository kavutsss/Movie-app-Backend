import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Force reset superuser password from env vars"

    def handle(self, *args, **kwargs):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip().lower()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        if not email or not password:
            self.stdout.write("Env vars not set, skipping.")
            return

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Password reset for: {email}"))
        except User.DoesNotExist:
            user = User.objects.create_superuser(email=email, password=password, name="Admin")
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {email}"))
