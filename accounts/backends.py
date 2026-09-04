from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows logging into Django Admin
    using either full email (case-insensitive) or 'admin' / username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if not username or not password:
            return None

        username = username.strip()

        # Try case-insensitive email match first
        user = User.objects.filter(email__iexact=username).first()

        # If not found by email and username is 'admin', try finding superuser/staff
        if not user and username.lower() == 'admin':
            user = User.objects.filter(is_staff=True).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
