from django.contrib import admin

from .models import Comment, Post, Report


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'movie_title', 'stars', 'status', 'created_at']
    list_filter = ['status', 'stars']
    search_fields = ['movie_title', 'body', 'user__email']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['body', 'user__email']
    list_editable = ['status']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reported_by', 'reason', 'status', 'created_at', 'resolved_by']
    list_filter = ['status', 'content_type']
    search_fields = ['reason', 'description', 'reported_by__email']
    readonly_fields = ['reported_by', 'content_type', 'object_id', 'created_at', 'resolved_at', 'resolved_by']
    ordering = ['-created_at']
