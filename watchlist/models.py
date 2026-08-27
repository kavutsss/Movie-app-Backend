from django.conf import settings
from django.db import models


class Watchlist(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
	movie_id = models.PositiveIntegerField()
	movie_title = models.CharField(max_length=255)
	poster_path = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		constraints = [models.UniqueConstraint(fields=['user', 'movie_id'], name='unique_watchlist_movie')]
