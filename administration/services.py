from .models import ActivityLog


def request_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return forwarded_for.split(',')[0].strip() if forwarded_for else request.META.get('REMOTE_ADDR')


def log_activity(request, event_type, actor=None, **fields):
    return ActivityLog.objects.create(
        actor=actor if actor is not None else (request.user if request.user.is_authenticated else None),
        event_type=event_type,
        ip_address=request_ip(request),
        **fields,
    )