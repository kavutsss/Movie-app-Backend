from django.urls import path

from .views import ClubDetailView, ClubListCreateView, ClubMembershipView

urlpatterns = [
    path('clubs/', ClubListCreateView.as_view(), name='club-list'),
    path('clubs/<int:pk>/', ClubDetailView.as_view(), name='club-detail'),
    path('clubs/<int:pk>/join/', ClubMembershipView.as_view(), name='club-membership'),
]