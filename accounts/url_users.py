from django.urls import path

from .views import FollowView, UserDetailView, UserListView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/follow/', FollowView.as_view(), name='user-follow'),
]