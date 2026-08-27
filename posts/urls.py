from django.urls import path

from .views import CommentDeleteView, CommentListCreateView, LikeView, PostDetailView, PostListCreateView

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', LikeView.as_view(), name='post-like'),
    path('posts/<int:pk>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
]