from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models


class Post(models.Model):
	class ModerationStatus(models.TextChoices):
		VISIBLE = 'VISIBLE', 'Visible'
		HIDDEN = 'HIDDEN', 'Hidden'
		REMOVED = 'REMOVED', 'Removed'

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
	movie_id = models.PositiveIntegerField()
	movie_title = models.CharField(max_length=255)
	body = models.TextField()
	stars = models.PositiveSmallIntegerField(null=True, blank=True)
	likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_posts')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=10, choices=ModerationStatus.choices, default=ModerationStatus.VISIBLE)

	class Meta:
		ordering = ['-created_at']


class Comment(models.Model):
	class ModerationStatus(models.TextChoices):
		VISIBLE = 'VISIBLE', 'Visible'
		HIDDEN = 'HIDDEN', 'Hidden'
		REMOVED = 'REMOVED', 'Removed'

	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=10, choices=ModerationStatus.choices, default=ModerationStatus.VISIBLE)

	class Meta:
		ordering = ['created_at']


class Report(models.Model):
	class Status(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		REVIEWED = 'REVIEWED', 'Reviewed'
		RESOLVED = 'RESOLVED', 'Resolved'
		DISMISSED = 'DISMISSED', 'Dismissed'

	reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_reports')
	content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
	object_id = models.PositiveBigIntegerField()
	target = GenericForeignKey('content_type', 'object_id')
	reason = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	resolved_at = models.DateTimeField(null=True, blank=True)
	resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='resolved_reports')

	class Meta:
		ordering = ['-created_at']
