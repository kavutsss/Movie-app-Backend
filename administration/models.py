from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    class EventType(models.TextChoices):
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        REGISTER = 'REGISTER', 'Registration'
        REVIEW_CREATED = 'REVIEW_CREATED', 'Review created'
        MOVIE_CHECKED = 'MOVIE_CHECKED', 'Movie checked'
        COMMENT_CREATED = 'COMMENT_CREATED', 'Comment created'
        LIKE_ADDED = 'LIKE_ADDED', 'Like added'
        LIKE_REMOVED = 'LIKE_REMOVED', 'Like removed'
        CLUB_CREATED = 'CLUB_CREATED', 'Club created'
        CLUB_JOINED = 'CLUB_JOINED', 'Club joined'
        CLUB_LEFT = 'CLUB_LEFT', 'Club left'
        WATCHLIST_ADDED = 'WATCHLIST_ADDED', 'Added to watchlist'
        WATCHLIST_REMOVED = 'WATCHLIST_REMOVED', 'Removed from watchlist'

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
    )
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    movie_id = models.PositiveIntegerField(null=True, blank=True)
    movie_title = models.CharField(max_length=255, blank=True)
    review = models.ForeignKey(
        'posts.Post',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['movie_id', '-created_at']),
        ]