from rest_framework.permissions import BasePermission


class IsPlatformAdmin(BasePermission):
    """Allow Django staff/superusers and members of the Administrators group."""

    message = 'Administrator access is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (
                user.is_staff or user.is_superuser or user.groups.filter(name='Administrators').exists()
            )
        )
