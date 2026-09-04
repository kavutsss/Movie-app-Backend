from rest_framework import generics, permissions

from administration.models import ActivityLog
from administration.services import log_activity
from .models import Watchlist
from .serializers import WatchlistSerializer


class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        watchlist = serializer.save(user=self.request.user)
        log_activity(self.request, ActivityLog.EventType.WATCHLIST_ADDED,
            movie_id=watchlist.movie_id, movie_title=watchlist.movie_title)


class WatchlistDetailView(generics.DestroyAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        log_activity(self.request, ActivityLog.EventType.WATCHLIST_REMOVED,
                     movie_id=instance.movie_id, movie_title=instance.movie_title)
        instance.delete()
