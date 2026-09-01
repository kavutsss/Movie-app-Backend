from django.urls import path

from .views import (AdminClubDetailView, AdminClubListView, AdminClubStatusView, AdminCommentDeleteView,
                    AdminCommentListView, AdminCommentModerateView, AdminPostDeleteView, AdminPostDetailView,
                    AdminPostListView, AdminPostModerateView, AdminReportDetailView, AdminReportListView,
                    AdminReviewListView, AdminUserDetailView, AdminUserListView, AdminUserStatusView,
                    AnalyticsView, DashboardView)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='admin-dashboard'),
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('users/<int:pk>/status/', AdminUserStatusView.as_view(), name='admin-user-status'),
    path('clubs/', AdminClubListView.as_view(), name='admin-club-list'),
    path('clubs/<int:pk>/', AdminClubDetailView.as_view(), name='admin-club-detail'),
    path('clubs/<int:pk>/status/', AdminClubStatusView.as_view(), name='admin-club-status'),
    path('posts/', AdminPostListView.as_view(), name='admin-post-list'),
    path('posts/<int:pk>/', AdminPostDetailView.as_view(), name='admin-post-detail'),
    path('posts/<int:pk>/moderate/', AdminPostModerateView.as_view(), name='admin-post-moderate'),
    path('posts/<int:pk>/delete/', AdminPostDeleteView.as_view(), name='admin-post-delete'),
    path('comments/', AdminCommentListView.as_view(), name='admin-comment-list'),
    path('comments/<int:pk>/moderate/', AdminCommentModerateView.as_view(), name='admin-comment-moderate'),
    path('comments/<int:pk>/delete/', AdminCommentDeleteView.as_view(), name='admin-comment-delete'),
    path('reviews/', AdminReviewListView.as_view(), name='admin-review-list'),
    path('reports/', AdminReportListView.as_view(), name='admin-report-list'),
    path('reports/<int:pk>/', AdminReportDetailView.as_view(), name='admin-report-detail'),
    path('analytics/', AnalyticsView.as_view(), name='admin-analytics'),
]
