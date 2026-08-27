from rest_framework import serializers

from .models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ['id', 'movie_id', 'movie_title', 'poster_path', 'created_at']
        read_only_fields = ['id', 'created_at']