from django.contrib import admin

from .models import Watchlist


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'movie_title', 'movie_id', 'created_at']
    search_fields = ['movie_title', 'user__email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
