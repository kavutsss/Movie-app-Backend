from django.urls import path

from .views import WatchlistDetailView, WatchlistListCreateView

urlpatterns = [
    path('watchlist/', WatchlistListCreateView.as_view(), name='watchlist-list'),
    path('watchlist/<int:pk>/', WatchlistDetailView.as_view(), name='watchlist-detail'),
]